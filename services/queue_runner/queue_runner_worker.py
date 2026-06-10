from __future__ import annotations

from typing import TYPE_CHECKING, Deque

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService
    from ..intra.intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
    from ..base.models import JobRequest
    from .models import QueueRunnerRequestPayload
    from ..browser import BrowserSessionFactory
    from services.browser.models import PlaywrightSession
    from services.profiles import ProfileRegistry

import time
from collections import deque
from threading import Event, get_ident

from PySide6.QtCore import QObject, Signal

from base.enums import INTRAVERSION
from services.auth.enums import PROVIDERS

from ..auth.enums import AUTHSTATUS
from ..auth.models.auth_result import AuthResult
from .enums import QUEUEEXECSTATUS, QUEUERUNNERLIFECYCLE, QUEUERUNSTATUS
from .executors import QueueExecutor
from .models import (
    QueueExecutionContext,
    QueueExecutionResult,
    QueueProgressEvent,
    QueueRunItem,
    QueueRunnerState,
)


class QueueRunnerWorker(QObject):
    done = Signal()
    progress = Signal(int, int)
    runner_result = Signal(object)
    task_progress = Signal(object)
    runner_life_cyle = Signal(object)

    def __init__(
        self,
        job: JobRequest[QueueRunnerRequestPayload],
        browser_session_factory: BrowserSessionFactory,
        session: IntraProviderSession,
        auth_service: AuthService,
        logger: LogAdapter,
        profile_registry: ProfileRegistry,
    ):
        super().__init__()
        self.q_item_queue: Deque[QueueRunItem] = deque(job.payload.queues)
        self.logger = logger
        self.session = session
        self.auth_service = auth_service
        self.browser_session_factory = browser_session_factory

        self.creds = job.payload.config
        self.url = f"https://{self.creds.tenant}.intradiem.com/"

        self.driver = None
        self.driver_adapter = None
        self.current_executor: QueueExecutor | None = None
        self.errored_queues: list[QueueRunItem] = []
        self.success_queues: list[QueueRunItem] = []
        self.completed_count = 0
        self.total_count = len(self.q_item_queue)
        self._shut_down = Event()

        self.playwright_session_manager = None
        self.playwright_session: PlaywrightSession | None = None
        self.profile_registry = profile_registry

        self.provider_name = job.payload.provider_name
        self.provider_instance = job.payload.provider_instance

    def should_stop(self) -> bool:
        return self._shut_down.is_set()

    def send_queue_progress(self, event: QueueProgressEvent):
        self.task_progress.emit(event)

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def do_work(self):
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {get_ident()}",
            "INFO",
        )
        try:
            self._init_browser(True)
            self.run_queue()

        except Exception as e:
            self.logging(f"{e}", "DEBUG")
            self.logging("Fatal Error", "ERROR")
        finally:
            self.runner_life_cyle.emit(QUEUERUNNERLIFECYCLE.FINISHED)
            self.clean_up()

    def _init_browser(self, load_session_cookies=False) -> None:
        """
        Initializes the Playwright.
        """
        self.playwright_session_manager = self.browser_session_factory.create_session(
            PROVIDERS.INTRA
        )
        self.playwright_session = self.playwright_session_manager.start()

    def _close_down_browser(self):
        if not self.playwright_session_manager:
            return
        self.playwright_session_manager.close()
        self.playwright_session_manager = None
        self.playwright_session = None

    def _rebuild_browser(self):
        self._close_down_browser()
        self._init_browser(load_session_cookies=False)

    def _authenticate(self) -> AuthResult:
        auth_attempts = 0
        max_attempts = 2

        while auth_attempts < max_attempts:
            if self.should_stop():
                return AuthResult(success=False, status=AUTHSTATUS.STOPPED_REQUESTED)
            self.logging(
                f"Attempting to authenticate: {auth_attempts} / {max_attempts-1}"
            )
            result = self.auth_service.ensure_auth(
                PROVIDERS.INTRA,
                self.creds,
                self.playwright_session.browser_adapter,
                should_stop_cb=self.should_stop,
            )

            if result.success:
                self.logging("Received Successful Authentication.")
                return result
            self.logging("Received Failure Authentication.", "WARN")
            if result.status == AUTHSTATUS.BROWSER_ERROR:
                self._rebuild_browser()
            auth_attempts += 1
        self.logging(
            "Attempted to log in 2 times. Login Failed due to an error.", "ERROR"
        )
        return result

    def _send_batch_progress(
        self,
        status: QUEUEEXECSTATUS,
        msg: str,
        start_time: bool = False,
        end_time: bool = False,
    ):
        for queue_item in self.q_item_queue:
            self.send_queue_progress(
                QueueProgressEvent(
                    queue_guid=queue_item.queue.guid,
                    queue_name=queue_item.queue.queue_name,
                    queue_row=queue_item.queue.row_number,
                    task=None,
                    status=status,
                    message=msg,
                    started_at=int(time.time()) if start_time else None,
                    finished_at=int(time.time()) if end_time else None,
                )
            )

    def run_queue(self):

        try:
            self.runner_life_cyle.emit(QUEUERUNNERLIFECYCLE.STARTED)
            self._send_batch_progress(QUEUEEXECSTATUS.PENDING, "Queue queued.")
            auth_result = self._authenticate()
            if auth_result.status == AUTHSTATUS.STOPPED_REQUESTED:
                self.stop_clean_up()
                return

            if not auth_result.success:
                self._shut_down.set()
                self._drain_remaining_rules(
                    QUEUERUNSTATUS.FAILED, "Failed to Authenticate"
                )
                return

            state = QueueRunnerState()
            while self.q_item_queue and not self.should_stop():
                self.progress.emit(self.completed_count, self.total_count)
                try:
                    item = self.q_item_queue.popleft()
                    item.status = QUEUERUNSTATUS.RUNNING
                    context = QueueExecutionContext(
                        tenant=self.creds.tenant,
                        provider_instance=self.provider_instance,
                        provider_name=self.provider_name,
                        browser_port=self.playwright_session.browser_adapter,
                        state=state,
                        queue=item.queue,
                        logger=self.logger,
                        should_stop=self.should_stop,
                        profile=self.profile_registry.get_profile(
                            INTRAVERSION(self.creds.platform_version)
                        ),
                        progress_cb=self.send_queue_progress,
                    )
                    self.send_queue_progress(
                        QueueProgressEvent(
                            queue_guid=item.queue.guid,
                            queue_name=item.queue.queue_name,
                            queue_row=item.queue.row_number,
                            task=None,
                            status=QUEUERUNSTATUS.RUNNING,
                            message="Started Run",
                            started_at=int(time.time()),
                        )
                    )
                    self.current_executor = QueueExecutor(queue_context=context)
                    result = self.current_executor.execute()
                    self._handle_result(item, result)
                except Exception as e:
                    if self.should_stop():
                        self.stop_clean_up()
                        return
                    self.logging(f"{e}", "DEBUG")
                    self.logging(
                        "Failure in queue. Trying to process next queue", "ERROR"
                    )
            if self.should_stop():
                self.stop_clean_up()
                return

        except Exception as e:
            if self.should_stop():
                self.stop_clean_up()
                return

            self.logging("Fatal Error Occurred. Shutting Down", "ERROR")
            self.logging(f"{e}", "ERROR")
        finally:
            self.create_rule_summary()

    def _send_result_progress(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        message: str,
        use_exec_status: bool = True,
    ):
        self.send_queue_progress(
            QueueProgressEvent(
                queue_guid=item.queue.guid,
                queue_name=item.queue.queue_name,
                queue_row=item.queue.row_number,
                task=result.task,
                status=result.status if use_exec_status else item.status,
                message=message,
                started_at=None,
                finished_at=int(time.time()),
            )
        )

    def _handle_result(self, item: QueueRunItem, result: QueueExecutionResult):
        self.logging(
            f"Recieved result for Row: {item.queue.row_number} - {item.queue.queue_name}"
        )
        if result.success:
            self.logging(
                f"Row: {item.queue.row_number} - {item.queue.queue_name} - succeeded."
            )
            item.status = QUEUERUNSTATUS.SUCCESS

            self.success_queues.append(item)
            self._send_result_progress(item, result, "Succeeded", use_exec_status=False)
            self.completed_count += 1
        else:
            if result.status == QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR:
                self._send_result_progress(
                    item, result, "Stop Requested", use_exec_status=True
                )
                self.errored_queues.append(item)
                self.completed_count = self.total_count
                self.logging("Queue Executor stopped.", "WARN")
                self.stop_clean_up()
                return

            self.logging(
                f"Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
            )
            if item.retry_count < 2:
                item.retry_count += 1
                if result.status in (QUEUEEXECSTATUS.NAME_EXISTS_ERROR):
                    item.status = QUEUERUNSTATUS.FAILED
                    self.errored_queues.append(item)
                    self.completed_count += 1
                    self.logging(
                        f"Row: {item.queue.row_number} - {item.queue.queue_name} - not retrying running queue."
                    )
                    self._send_result_progress(
                        item,
                        result,
                        "Queue Name Exists Already.",
                        use_exec_status=False,
                    )
                elif result.status in (
                    QUEUEEXECSTATUS.BROWSER_ERROR,
                    QUEUEEXECSTATUS.UNKNOWN_ERROR,
                ):

                    self.logging(
                        f"Row: {item.queue.row_number} - {item.queue.queue_name} - retrying running queue."
                    )
                    item.status = QUEUERUNSTATUS.RETRYING
                    self.q_item_queue.appendleft(item)
                    self._send_result_progress(
                        item, result, "Retrying...", use_exec_status=False
                    )
                    self._rebuild_browser()
                    auth_result = self._authenticate()
                    if not auth_result.success:
                        self._shut_down.set()
                        self._drain_remaining_rules(
                            QUEUERUNSTATUS.FAILED, "Authentication failed during retry"
                        )
                        return
            else:
                self.logging(
                    f"Row: {item.queue.row_number} - {item.queue.queue_name} - not retrying running queue."
                )
                item.status = QUEUERUNSTATUS.FAILED
                self._send_result_progress(
                    item, result, "Failed. Not retrying.", use_exec_status=False
                )
                self.errored_queues.append(item)
                self.completed_count += 1

    def create_rule_summary(self) -> None:
        """
        Creates a summary of successfully executed and errored queues.
        """
        errored_rules_msg = f"ERRORED Queues TOTAL: {len(self.errored_queues)} \n"
        succeeded_rules_msg = f"SUCCEEDED Queues TOTAL: {len(self.success_queues)} \n"
        tabs = "\t" * 3
        for error_rule in self.errored_queues:
            errored_rules_msg += f"{tabs}- Row {error_rule.queue.row_number}: - {error_rule.queue.queue_name} \n"
        for succeed_rule in self.success_queues:
            succeeded_rules_msg += f"{tabs}- Row {succeed_rule.queue.row_number}: - {succeed_rule.queue.queue_name} \n"
        self.logging(succeeded_rules_msg, "INFO")
        self.logging(errored_rules_msg, "ERROR")

    def _drain_remaining_rules(self, status: QUEUERUNSTATUS, reason: str):
        while self.q_item_queue:
            self._send_batch_progress(status, reason, end_time=True)
            item = self.q_item_queue.popleft()
            item.status = status
            self.errored_queues.append(item)

        self.logging(f"Removing remaining queues from queue: {reason}", "WARN")

    def stop_clean_up(self):
        self._drain_remaining_rules(
            QUEUERUNSTATUS.STOPPED, "Queue Runner manually stopped."
        )
        self.progress.emit(self.total_count, self.total_count)

    def stop(self) -> None:
        """
        Stops the thread execution.
        """
        self.logging("Stop Button Pressed", "INFO")
        self.logging("Shutting down", "INFO")
        self._shut_down.set()

    def clean_up(self) -> None:
        """
        Closes the thread and ensures proper shutdown of all resources.
        """
        self._close_down_browser()
        self.done.emit()
