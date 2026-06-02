from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from ..models import QueueExecutionContext

import threading

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ..enums import QUEUEEXECSTATUS, QEXECUTORTASK
from base.errors import (
    DuplicateNameException,
    PlaywrightSessionLostException,
    StoppedRequestException,
)
from ..models import QueueExecutionResult, QueueProgressEvent, QEXECSTEPCALL


class QueueExecutor:
    """ """

    def __init__(self, queue_context: QueueExecutionContext):
        self._ctx = queue_context
        self._current_task: QEXECUTORTASK = QEXECUTORTASK.START
        self._interaction_port = None
        self._flow = []

    @property
    def form_port(self) -> InteractionPort:
        if self._interaction_port is None:
            raise RuntimeError("Queue form interaction port has not been initialized.")
        return self._interaction_port

    @form_port.setter
    def form_port(self, form: InteractionPort):
        self._interaction_port = form

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self._ctx.logger(msg, level, print_msg)

    def queue_progress(
        self, task: QEXECUTORTASK, status: QUEUEEXECSTATUS, message=None
    ):
        self._ctx.progress_cb(
            QueueProgressEvent(
                queue_guid=self._ctx.queue.guid,
                queue_name=self._ctx.queue.queue_name,
                task=task,
                status=status,
                message=message,
            )
        )

    def run_step(self, step: QEXECSTEPCALL):
        self._current_task = step.task
        self.queue_progress(step.task, QUEUEEXECSTATUS.RUNNING)
        if self._ctx.should_stop():
            raise StoppedRequestException("Stop Requested")
        try:
            handler = step.handler
            handler(self._ctx)
        except Exception as e:
            print(e)
            if self._ctx.should_stop():
                self.queue_progress(step.task, QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR)
                raise StoppedRequestException("Stop Requested") from e

            self.queue_progress(step.task, QUEUEEXECSTATUS.UNKNOWN_ERROR)
            raise
        self.queue_progress(step.task, QUEUEEXECSTATUS.SUCCESS)

    def execute(self) -> QueueExecutionResult:
        """
        Executes the queue creation process by navigating through the form pages and submitting queues.
        """

        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )

            for step in self._flow:
                self.run_step(step)

            return QueueExecutionResult(
                queue_guid=self._ctx.queue.guid,
                queue_name=self._ctx.queue.queue_name,
                queue_row=self._ctx.queue.row_number,
                success=True,
                task=self._current_task,
                status=QUEUEEXECSTATUS.SUCCESS,
                message="Queue submitted successfully.",
            )
        except StoppedRequestException:
            return self._build_error_result(
                status=QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR,
                message="Stopped Requested.",
            )

        except DuplicateNameException:
            return self._build_error_result(
                status=QUEUEEXECSTATUS.NAME_EXISTS_ERROR,
                message="Queue name already exists.",
            )

        except PlaywrightSessionLostException as e:

            if self._ctx.should_stop():
                return self._build_error_result(
                    status=QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR,
                    message="Stopped Requested.",
                )
            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                status=QUEUEEXECSTATUS.BROWSER_ERROR,
                message="Browser doesnt exist.",
            )

        except PlaywrightTimeoutError as e:
            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                status=QUEUEEXECSTATUS.TIMEOUT_ERROR,
                message="Finding element timed out. Queue Failed.",
            )

        except PlaywrightError as e:
            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                status=QUEUEEXECSTATUS.BROWSER_ERROR,
                message="Browser error occurred.",
            )

        except Exception as e:

            if self._ctx.should_stop():
                return self._build_error_result(
                    status=QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR,
                    message="Stopped Requested.",
                )

            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                status=QUEUEEXECSTATUS.UNKNOWN_ERROR,
                message="Error happened in Queue execution.",
            )

    def _build_error_result(self, status: QUEUEEXECSTATUS, message: str):
        self.logging(message, "ERROR")
        return QueueExecutionResult(
            queue_guid=self._ctx.queue.guid,
            queue_name=self._ctx.queue.queue_name,
            queue_row=self._ctx.queue.row_number,
            success=False,
            task=self._current_task,
            status=status,
            message=message,
        )
