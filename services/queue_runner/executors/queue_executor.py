from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from ..models import QueueExecutionContext

import threading

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from base.errors import (
    DuplicateNameException,
    PlaywrightSessionLostException,
    StoppedRequestException,
)

from ..enums import QEXECUTORTASK, QUEUEEXECSTATUS
from ..models import QEXECSTEPCALL, QueueExecutionResult, QueueProgressEvent


class QueueExecutor:
    """
    Queue Executor runs the tasks of navigating to the queue entry form for a provider and inputting a queue.
    If the form is already open, the executor will skip the navigation to the form and directly input the queue.
    """

    def __init__(self, queue_context: QueueExecutionContext):
        self._ctx = queue_context
        self._current_task: QEXECUTORTASK = QEXECUTORTASK.START
        self._interaction_port = None

        self._ensure_form_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.FIND_PROVIDER_NAME, self.find_provider_name),
            QEXECSTEPCALL(QEXECUTORTASK.OPEN_PROVIDER_FORM, self.open_provider_form),
            QEXECSTEPCALL(
                QEXECUTORTASK.FIND_PROVIDER_INSTANCE, self.find_provider_instance
            ),
            QEXECSTEPCALL(
                QEXECUTORTASK.SWITCH_TO_INSTANCE_CONFIG,
                self.switch_to_configuration_page,
            ),
            QEXECSTEPCALL(
                QEXECUTORTASK.OPEN_QUEUE_FORM,
                self.open_queue_form,
            ),
        ]

        self._queue_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.SET_QUEUE_NAME, self.set_queue_name),
            QEXECSTEPCALL(QEXECUTORTASK.SET_QUEUE_NUMBER, self.set_queue_number),
            QEXECSTEPCALL(QEXECUTORTASK.SUBMIT_QUEUE, self.submit_queue),
            QEXECSTEPCALL(
                QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_queue_submission
            ),
        ]

    @property
    def form_port(self) -> InteractionPort:
        if self._ctx.state.form_port is None:
            raise RuntimeError("Form port has not been initialized.")
        return self._ctx.state.form_port

    @property
    def queue_port(self) -> InteractionPort:
        if self._ctx.state.queue_port is None:
            raise RuntimeError("Queue form port has not been initialized.")
        return self._ctx.state.queue_port

    def _is_queue_form_usable(self):
        if self._ctx.state.queue_port is None:
            return False
        try:
            return self._ctx.state.queue_port.is_visible(
                self._ctx.profile.selectors.queues.queue_name_input,
                timeout=1000,
            )
        except Exception:
            self._ctx.state.queue_port = None
            return False

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
                queue_row=self._ctx.queue.row_number,
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

    def set_queue_number(self, ctx: QueueExecutionContext):
        self.queue_port.fill(
            ctx.profile.selectors.queues.queue_number_input,
            str(ctx.queue.queue_number),
        )

    def set_queue_name(self, ctx: QueueExecutionContext):
        self.queue_port.fill(
            ctx.profile.selectors.queues.queue_name_input,
            ctx.queue.queue_name,
        )

    def submit_queue(self, ctx: QueueExecutionContext):
        alert = ctx.browser_port.frame_click_and_accept_alert_if_appears(
            self.queue_port, ctx.profile.selectors.queues.queue_add_btn
        )
        self.logging(f"Submitted Queue: {ctx.queue.queue_number}", "INFO")
        if alert:
            raise DuplicateNameException
        self.logging("Checking for Loading Spinner.", "INFO")
        self.queue_port.wait_for_loading_cycle(
            ctx.profile.selectors.queues.queue_grid_container,
            500,
            disappear_timeout=30000,
        )
        self.logging("Loading Spinner Clear.", "INFO")

    def verify_queue_submission(self, ctx: QueueExecutionContext):
        self.logging("Verification started", "INFO")
        self.logging("Finding Name Row", "INFO")
        name_row = self.queue_port.find_by_has_selector(
            ctx.profile.selectors.queues.queue_grid_rows,
            (
                f"{ctx.profile.selectors.queues.queue_row_name_item}"
                f"[{ctx.profile.selectors.queues.queue_row_attribute}="
                f"'{ctx.queue.queue_name}']"
            ),
        )
        self.logging("Getting queue number", "INFO")
        try:
            actual_number = self.queue_port.get_attribute_inside_parent(
                name_row,
                selector=ctx.profile.selectors.queues.queue_row_number_item,
                attribute=ctx.profile.selectors.queues.queue_row_attribute,
                timeout=3000,
            )
        except PlaywrightTimeoutError:
            actual_number = self.queue_port.get_attribute_inside_parent(
                name_row,
                selector=ctx.profile.selectors.queues.queue_row_number_item,
                attribute=ctx.profile.selectors.queues.queue_row_attribute,
                timeout=10000,
            )
        expected_number = str(ctx.queue.queue_number)
        expected_name = str(ctx.queue.queue_name)

        if actual_number != expected_number and actual_number != expected_name:
            msg = f"""Queue save verification failed. \n
                Expected number {expected_number!r} or {expected_name!r}, got {actual_number!r}"""
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        self.logging("Queue number found")

    def execute(self) -> QueueExecutionResult:
        """
        Executes the queue creation process by navigating through the form pages and submitting queues.
        """

        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )
            self._ctx.browser_port.wait_for_page_ready()

            if not self._is_queue_form_usable():
                for step in self._ensure_form_flow:
                    self.run_step(step)

            for step in self._queue_flow:
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

    # ***********************************************
    # ENSURE FORM HANDLERS

    def find_provider_name(self, ctx: QueueExecutionContext):
        path = f"https://{ctx.tenant}.intradiem.com/{ctx.profile.selectors.providers.page_path}"
        if not ctx.browser_port.is_current_url(url_part=path, exact=True):
            ctx.browser_port.goto(
                f"https://{ctx.tenant}.intradiem.com/{ctx.profile.selectors.providers.page_path}"
            )
        provider_category = ctx.browser_port.find_by_has_text(
            ctx.profile.selectors.providers.category_items,
            ctx.profile.selectors.providers.category_header,
            ctx.profile.selectors.providers.acd_category_title,
            True,
        )

        provider_instance = ctx.browser_port.find_child_by_has_text(
            provider_category,
            ctx.profile.selectors.providers.provider_cards,
            ctx.profile.selectors.providers.provider_name,
            ctx.provider_name,
            True,
        )

        ctx.browser_port.click_inside_parent(
            provider_instance,
            ctx.profile.selectors.providers.provider_edit_button,
            no_wait_after=True,
        )

    def open_provider_form(self, ctx: QueueExecutionContext):
        frame_port = ctx.browser_port.frame_locator(
            ctx.profile.selectors.provider_instance.provider_modal_frame
        )
        ctx.state.form_port = frame_port

    def find_provider_instance(self, ctx: QueueExecutionContext):
        self.form_port.click(ctx.profile.selectors.provider_instance.instances_button)

        self.form_port.click(
            ctx.profile.selectors.provider_instance.provider_instance_dropdown_arrow
        )

        ctx.browser_port.frame_select_from_list_and_accept_alert_if_appears(
            self.form_port,
            ctx.profile.selectors.provider_instance.provider_instance_dropdown_items,
            ctx.provider_instance,
        )

    def switch_to_configuration_page(self, ctx: QueueExecutionContext):
        self.form_port.click(
            ctx.profile.selectors.provider_instance.configuration_button
        )

    def open_queue_form(self, ctx: QueueExecutionContext):
        manage_queues = self.form_port.find_by_has_text(
            ctx.profile.selectors.provider_instance.configuration_items,
            ctx.profile.selectors.provider_instance.configuration_header,
            ctx.profile.selectors.provider_instance.manage_queues_btn_text,
            True,
        )

        self.form_port.click_inside_parent(
            manage_queues,
            ctx.profile.selectors.provider_instance.configuration_field_button,
        )

        queue_port = self.form_port.frame_locator(
            ctx.profile.selectors.queues.queues_modal_frame
        )
        ctx.state.queue_port = queue_port
