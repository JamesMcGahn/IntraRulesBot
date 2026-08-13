from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from ..models import QueueExecutionContext
    from ...api.queues.queue_v11_api import V11QueueApi

import threading

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from base.errors import (
    DuplicateNameException,
    PlaywrightSessionLostException,
    StoppedRequestException,
    QueueNotFound,
    ProviderNotFound,
    ProviderInstanceNotFound,
)

from ..enums import QEXECUTORTASK, QUEUEEXECSTATUS
from ..models import QEXECSTEPCALL, QueueExecutionResult, QueueProgressEvent
from services.queues.enums import QUEUEACTION


class V11QueueExecutor:
    """
    Queue Executor runs the tasks of navigating to the queue entry form for a provider and inputting a queue.
    If the form is already open, the executor will skip the navigation to the form and directly input the queue.
    """

    def __init__(self, queue_context: QueueExecutionContext, queue_api: V11QueueApi):
        self._ctx = queue_context
        self._current_task: QEXECUTORTASK = QEXECUTORTASK.START
        self._interaction_port = None
        self._queue_api = queue_api
        self._ensure_form_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.FIND_PROVIDER_NAME, self.find_provider_name),
            QEXECSTEPCALL(
                QEXECUTORTASK.FIND_PROVIDER_INSTANCE, self.find_provider_instance
            ),
            # QEXECSTEPCALL(
            #     QEXECUTORTASK.SWITCH_TO_INSTANCE_CONFIG,
            #     self.switch_to_configuration_page,
            # ),
            # QEXECSTEPCALL(
            #     QEXECUTORTASK.OPEN_QUEUE_FORM,
            #     self.open_queue_form,
            # ),
        ]

        self._add_queue_flow = [
            # QEXECSTEPCALL(QEXECUTORTASK.SET_QUEUE_NAME, self.set_queue_name),
            # QEXECSTEPCALL(QEXECUTORTASK.SET_QUEUE_NUMBER, self.set_queue_number),
            # QEXECSTEPCALL(QEXECUTORTASK.SUBMIT_QUEUE, self.submit_queue),
            # QEXECSTEPCALL(
            #     QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_queue_submission
            # ),
        ]

        self._del_queue_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.DELETE_QUEUE, self.delete_queue),
            QEXECSTEPCALL(QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_delete_queue),
        ]

        self._verify_add_queue_flow = [
            QEXECSTEPCALL(
                QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_queue_submission
            ),
        ]

        self._verify_del_queue_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_delete_queue),
        ]

        self._queue_actions = {
            QUEUEACTION.ADD: self._add_queue_flow,
            QUEUEACTION.VERIFY_EXISTS: self._verify_add_queue_flow,
            QUEUEACTION.VERIFY_NOT_EXISTS: self._verify_del_queue_flow,
            QUEUEACTION.DELETE: self._del_queue_flow,
        }

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
        self.logging("Checking the Provider Modal is Open.", "DEBUG")
        if self._ctx.state.queue_port is None:
            return False

        try:
            self._ctx.state.queue_port.wait_for_loading_cycle(
                self._ctx.profile.selectors.queues.queue_grid_container,
                500,
                disappear_timeout=45_000,
            )

            return self._ctx.state.queue_port.is_visible(
                self._ctx.profile.selectors.queues.queue_name_input,
                timeout=5_000,
            )
        except PlaywrightTimeoutError:
            # The frame may still exist, form never became usable.
            return False

        except PlaywrightError:
            # The cached frame is actually detached, closed, or otherwise invalid.
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
            self.queue_port, ctx.profile.selectors.queues.queue_add_button
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
                timeout=20_000,
            )
        expected_number = str(ctx.queue.queue_number)
        expected_name = str(ctx.queue.queue_name)

        if actual_number != expected_number and actual_number != expected_name:
            msg = f"""Queue save verification failed. \n
                Expected number {expected_number!r} or {expected_name!r}, got {actual_number!r}"""
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        self.logging("Queue number found")

    def delete_queue(self, ctx: QueueExecutionContext):
        message = f"Unable to find {ctx.queue.queue_name}. Queue does not exist"
        try:
            name_row = self.queue_port.find_by_has_selector(
                ctx.profile.selectors.queues.queue_grid_rows,
                (
                    f"{ctx.profile.selectors.queues.queue_row_name_item}"
                    f"[{ctx.profile.selectors.queues.queue_row_attribute}="
                    f"'{ctx.queue.queue_name}']"
                ),
            )
            if name_row.count() == 0:
                self.logging(message, "ERROR")
                raise QueueNotFound

            ctx.browser_port.frame_click_and_accept_alert_if_appears(
                name_row,
                ctx.profile.selectors.queues.queue_delete_button,
                "delete",
            )

            self.logging("Checking for Loading Spinner.", "INFO")
            self.queue_port.wait_for_loading_cycle(
                ctx.profile.selectors.queues.queue_grid_container,
                500,
                disappear_timeout=30000,
            )
            self.logging("Loading Spinner Clear.", "INFO")
        except PlaywrightTimeoutError as e:
            self.logging(message, "ERROR")
            raise QueueNotFound from e

    def verify_delete_queue(self, ctx: QueueExecutionContext):
        name_row = self.queue_port.find_by_has_selector(
            ctx.profile.selectors.queues.queue_grid_rows,
            (
                f"{ctx.profile.selectors.queues.queue_row_name_item}"
                f"[{ctx.profile.selectors.queues.queue_row_attribute}="
                f"'{ctx.queue.queue_name}']"
            ),
        )
        try:
            self.queue_port.verify_locator_not_present(name_row, 3000)
        except (PlaywrightTimeoutError, AssertionError):
            self.queue_port.verify_locator_not_present(name_row, 30_000)

    def execute(self) -> QueueExecutionResult:
        """
        Executes the queue creation process by navigating through the form pages and submitting queues.
        """

        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )
            # self._ctx.browser_port.wait_for_page_ready()

            # if not self._is_queue_form_usable():
            #     self.logging("Provider Modal is not open. Reopening Modal", "INFO")
            print("******v111")
            for step in self._ensure_form_flow:
                self.run_step(step)
            self.logging("Provider Modal is open. Continuing", "INFO")
            action_type = self._ctx.action_type
            queue_flow = self._queue_actions.get(action_type)

            if queue_flow is None:
                msg = f"queue_action is not a recognized value. value: {queue_flow}"
                self.logging(msg, "ERROR")
                raise ValueError(msg)
            for step in queue_flow:
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

        except QueueNotFound:
            return self._build_error_result(
                status=QUEUEEXECSTATUS.QUEUE_NOT_FOUND_ERROR,
                message="Queue not found.",
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
        self.logging(f"Trying to Find Provider Name: {ctx.provider_name}", "INFO")
        providers = self._queue_api.get_providers(ctx.tenant)
        is_provider = [
            provider
            for provider in providers
            if provider.name.lower() == ctx.provider_name.lower()
        ]
        print(is_provider)
        if is_provider:
            ctx.state.provider_info = is_provider[0]
            self.logging(f"Found Provider Name: {ctx.provider_name}", "INFO")
        else:
            raise ProviderNotFound(
                f"Provider Name: {ctx.provider_name} does not exist."
            )

    def find_provider_instance(self, ctx: QueueExecutionContext):
        self.logging(
            f"Trying to Find Provider Instance: {ctx.provider_instance}", "INFO"
        )

        instances = self._queue_api.get_provider_instances(
            ctx.tenant, ctx.state.provider_info
        )
        print(instances)
        print("8888888888888888")
        is_instance = [
            instance
            for instance in instances
            if instance.name.lower() == ctx.provider_instance.lower()
        ]
        print("8888888888888888")
        print(is_instance)
        if is_instance:
            ctx.state.provider_instance = is_instance[0]
            self.logging(f"Found Provider Instance: {ctx.provider_instance}", "INFO")
        else:
            raise ProviderInstanceNotFound(
                f"Provider Instance Name: {ctx.provider_instance} does not exist."
            )

    def switch_to_configuration_page(self, ctx: QueueExecutionContext):
        self.logging(
            f"Switching Provider Instance {ctx.provider_instance} Configuration Page.",
            "INFO",
        )
        self.form_port.click(
            ctx.profile.selectors.provider_instance.configuration_button
        )

    def open_queue_form(self, ctx: QueueExecutionContext):
        self.logging(
            f"Opening Provider Instance: {ctx.provider_instance} Queue Form", "INFO"
        )
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
        self.logging(f"{ctx.provider_instance} Queue Form Opened.", "INFO")
