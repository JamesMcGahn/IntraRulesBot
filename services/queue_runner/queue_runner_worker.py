from __future__ import annotations

from typing import TYPE_CHECKING, Deque

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService
    from ..intra.v10.intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
    from ..base.models import JobRequest
    from .models import QueueRunnerRequestPayload
    from ..browser import BrowserSessionFactory
    from services.browser.models import PlaywrightSession
    from services.profiles import ProfileRegistry
    from ..api.queues.queue_v11_api import V11QueueApi

import time
from collections import deque
from threading import Event, get_ident

from PySide6.QtCore import QObject, Signal

from base.enums import INTRAVERSION

from ..auth.enums import AUTHSTATUS
from ..auth.models.auth_result import AuthResult
from .enums import (
    QUEUEEXECSTATUS,
    QUEUERUNNERLIFECYCLE,
    QUEUERUNSTATUS,
    QEXECUTORTASK,
    QRECOVERYACTION,
    QRESULTACTION,
)
from .executors import QueueExecutor, V11QueueExecutor
from .models import (
    QueueExecutionContext,
    QueueExecutionResult,
    QueueProgressEvent,
    QueueRunItem,
    QueueRunnerState,
)
from services.queues.enums import QUEUEACTION
from .queue_result_handler import QueueResultHandler


class QueueRunnerWorker(QObject):
    done = Signal()
    task_progress = Signal(object)
    runner_life_cyle = Signal(object)
    progress_status = Signal(int, int)

    def __init__(
        self,
        job: JobRequest[QueueRunnerRequestPayload],
        browser_session_factory: BrowserSessionFactory,
        session: IntraProviderSession,
        auth_service: AuthService,
        logger: LogAdapter,
        profile_registry: ProfileRegistry,
        queue_api: V11QueueApi,
    ):
        super().__init__()
        self.q_item_queue: Deque[QueueRunItem] = deque(job.payload.queues)
        self.logger = logger
        self.session = session
        self.auth_service = auth_service
        self.browser_session_factory = browser_session_factory
        self._queue_api = queue_api

        self.creds = job.payload.config
        self.url = f"https://{self.creds.tenant}.intradiem.com/"

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
        self._result_handler = QueueResultHandler(
            logging=self.logging,
            send_result_progress=self._send_result_progress,
            platform_version=self.creds.platform_version,
        )
        try:
            self._init_browser(True)
            self.run_queue()

        except Exception as e:
            self.logging(f"{e}", "DEBUG")
            self.logging("Fatal Error", "ERROR")
            if self.should_stop():
                self._drain_remaining_queues(
                    QUEUERUNSTATUS.STOPPED,
                    "Queue Runner manually stopped.",
                )
            else:
                self._drain_remaining_queues(
                    QUEUERUNSTATUS.FAILED,
                    "Fatal queue runner error.",
                )
        finally:
            self.runner_life_cyle.emit(QUEUERUNNERLIFECYCLE.FINISHED)
            self.clean_up()

    def _init_browser(self, load_session_cookies=False) -> None:
        """
        Initializes the Playwright.
        """

        self.playwright_session_manager = self.browser_session_factory.create_session(
            self.session.provider_name
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
                self.session.provider_name,
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
        # TODO : REMOVE : TOO MANY SIGNALS - BAD
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
            # self._send_batch_progress(QUEUEEXECSTATUS.PENDING, "Queue queued.")
            auth_result = self._authenticate()
            if auth_result.status == AUTHSTATUS.STOPPED_REQUESTED:
                self.stop_clean_up()
                return

            if not auth_result.success:
                self._drain_remaining_queues(
                    QUEUERUNSTATUS.FAILED, "Failed to Authenticate"
                )
                return

            state = QueueRunnerState()
            self.total_count = len(self.q_item_queue)
            self.logging(f"Total Queues: {len(self.q_item_queue)}", "INFO")
            self.progress_status.emit(0, self.total_count)
            while self.q_item_queue and not self.should_stop():
                item: QueueRunItem | None = None
                self.logging(
                    f"({self.completed_count+1}/{self.total_count}) - Queue Executing"
                )
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
                        action_type=item.action_type,
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

                    if INTRAVERSION.V10 == self.creds.platform_version:
                        self.current_executor = QueueExecutor(queue_context=context)
                    elif INTRAVERSION.V11 == self.creds.platform_version:
                        self.current_executor = V11QueueExecutor(
                            queue_context=context, queue_api=self._queue_api
                        )
                    else:
                        msg = f"{self.creds.platform_version} does not have a supported executor"
                        self.logging(msg, "ERROR")
                        raise ValueError(msg)
                    result = self.current_executor.execute()
                    self._process_result(item, result)
                except Exception as e:
                    if self.should_stop():
                        if item is not None:
                            self.q_item_queue.appendleft(item)
                        self.stop_clean_up()
                        return
                    self.logging(f"{e}", "DEBUG")
                    self.logging(
                        "Failure in queue. Trying to process next queue", "ERROR"
                    )
                    if item is not None:
                        result = QueueExecutionResult(
                            queue_guid=item.queue.guid,
                            queue_name=item.queue.queue_name,
                            queue_row=item.queue.row_number,
                            success=False,
                            task=QEXECUTORTASK.START,
                            status=QUEUEEXECSTATUS.FATAL_ERROR,
                            message="Fatal Error: Failure in queue",
                        )
                        self._process_result(item, result)

            if self.should_stop():
                self.stop_clean_up()
                return

        except Exception as e:
            if self.should_stop():
                self.stop_clean_up()
                return

            self.logging("Fatal Error Occurred. Shutting Down", "ERROR")
            self.logging(f"{e}", "ERROR")
            self._drain_remaining_queues(
                QUEUERUNSTATUS.FAILED,
                "Fatal queue runner error.",
            )
        finally:
            self.create_queue_summary()

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
                retry_count=item.retry_count,
                status=result.status if use_exec_status else item.status,
                message=message,
                started_at=None,
                finished_at=int(time.time()),
            )
        )

    def _process_result(self, item: QueueRunItem, result: QueueExecutionResult):

        decision = self._result_handler.handle_result(
            item, result, self.completed_count + 1, self.total_count
        )

        if decision.action == QRESULTACTION.SUCCESS:
            self.success_queues.append(item)
            self.completed_count += 1
        elif decision.action == QRESULTACTION.STOP:
            self.errored_queues.append(item)
            self.completed_count = self.total_count
            self.stop_clean_up()
            return
        elif decision.action == QRESULTACTION.ABORT_RUN:
            self.errored_queues.append(item)
            self.completed_count = self.total_count
            self._drain_remaining_queues(
                QUEUERUNSTATUS.FAILED,
                "Queue Runner stopped. Too many consecutive errors.",
            )
            return
        elif decision.action == QRESULTACTION.RETRY:

            if decision.recovery == QRECOVERYACTION.NONE:
                self.q_item_queue.appendleft(item)
                return

            elif decision.recovery == QRECOVERYACTION.REBUILD_BROWSER:
                self._rebuild_browser()
                auth_result = self._authenticate()
                if auth_result.status == AUTHSTATUS.STOPPED_REQUESTED:
                    self.q_item_queue.appendleft(item)
                    return
                if not auth_result.success:
                    self.q_item_queue.appendleft(item)
                    self._drain_remaining_queues(
                        QUEUERUNSTATUS.FAILED, "Authentication failed during retry"
                    )
                    return
                self.q_item_queue.appendleft(item)
            elif decision.recovery == QRECOVERYACTION.AUTHENTICATE:
                auth_result = self._authenticate()
                if auth_result.status == AUTHSTATUS.STOPPED_REQUESTED:
                    self.q_item_queue.appendleft(item)
                    return

                if not auth_result.success:
                    self.q_item_queue.appendleft(item)
                    self._drain_remaining_queues(
                        QUEUERUNSTATUS.FAILED, "Authentication failed during retry"
                    )
                    return
                self.q_item_queue.appendleft(item)
        elif decision.action == QRESULTACTION.FAIL:
            self.errored_queues.append(item)
            self.completed_count += 1

        self.progress_status.emit(self.completed_count, self.total_count)

    def create_queue_summary(self) -> None:
        """
        Creates a summary of successfully executed and errored queues.
        """
        errored_queues_msg = f"ERRORED Queues TOTAL: {len(self.errored_queues)} \n"
        succeeded_queues_msg = f"SUCCEEDED Queues TOTAL: {len(self.success_queues)} \n"
        tabs = "\t" * 3
        for error_rule in self.errored_queues:
            errored_queues_msg += f"{tabs}- Row {error_rule.queue.row_number}: - {error_rule.queue.queue_name} \n"
        for succeed_rule in self.success_queues:
            succeeded_queues_msg += f"{tabs}- Row {succeed_rule.queue.row_number}: - {succeed_rule.queue.queue_name} \n"
        self.logging(succeeded_queues_msg, "INFO")
        self.logging(errored_queues_msg, "ERROR")

    def _drain_remaining_queues(self, status: QUEUERUNSTATUS, reason: str):
        # self._send_batch_progress(status, reason, end_time=True)
        while self.q_item_queue:
            item = self.q_item_queue.popleft()
            item.status = status
            self.errored_queues.append(item)
        self.progress_status.emit(self.total_count, self.total_count)

        self.logging(f"Removing remaining queues from queue: {reason}", "WARN")

    def stop_clean_up(self):
        self._drain_remaining_queues(
            QUEUERUNSTATUS.STOPPED, "Queue Runner manually stopped."
        )

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
