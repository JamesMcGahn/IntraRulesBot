from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from ..models import QueueExecutionContext
    from ...api.queues.queue_v11_api import V11QueueApi

import threading

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from base.errors import (
    DuplicateNameException,
    StoppedRequestException,
    QueueNotFound,
    ProviderNotFound,
    ProviderInstanceNotFound,
    NotAuthenticatedException,
    RetryableNetworkException,
    NetworkResponseException,
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
            QEXECSTEPCALL(
                QEXECUTORTASK.FIND_PROVIDER_CUSTOM_RESOURCES,
                self.find_queue_custom_resource,
            ),
        ]

        self._add_queue_flow = [
            QEXECSTEPCALL(
                QEXECUTORTASK.CHECK_FOR_DUPLICATE_QUEUE, self.check_duplicate_queue
            ),
            QEXECSTEPCALL(QEXECUTORTASK.SUBMIT_QUEUE, self.submit_queue),
            QEXECSTEPCALL(
                QEXECUTORTASK.GET_CURRENT_PROVIDER_INSTANCE,
                self.get_current_provider_instance,
            ),
            QEXECSTEPCALL(
                QEXECUTORTASK.UPDATE_PROVIDER_INSTANCE_SETTINGS,
                self.submit_provider_settings,
            ),
            QEXECSTEPCALL(QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_queue_added),
        ]

        self._del_queue_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.DELETE_QUEUE, self.delete_queue),
            QEXECSTEPCALL(QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_delete_queue),
        ]

        self._verify_add_queue_flow = [
            QEXECSTEPCALL(QEXECUTORTASK.VERIFY_SUBMISSION, self.verify_queue_added),
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

    def _is_provider_settings_usable(self, ctx: QueueExecutionContext):
        self.logging("Checking the Provider Settings Cache.", "DEBUG")
        if ctx.state.provider_instance is None:
            return False

        if ctx.state.queue_custom_resource is None:
            return False

        if ctx.state.provider_info is None:
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
        self.logging(f"Submitting Queue: {ctx.queue.queue_number}", "INFO")
        self._queue_api.add_queue(
            ctx.tenant,
            ctx.state.queue_custom_resource,
            ctx.state.provider_instance,
            ctx.queue,
        )

    # TODO - Make Delete Flow
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

    # TODO - Make Delete Flow
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

    def get_current_provider_instance(self, ctx: QueueExecutionContext):
        self.logging(
            f"Getting Current Provider Instance Settings: {ctx.provider_instance}",
            "INFO",
        )

        instance = self._queue_api.get_provider_instance(
            ctx.tenant, ctx.state.provider_instance
        )

        if instance.id != ctx.state.provider_instance.id:
            raise ProviderInstanceNotFound(
                f"Provider Instance Name: {ctx.provider_instance} does not exist."
            )

        ctx.state.provider_instance = instance

    def submit_provider_settings(self, ctx: QueueExecutionContext):
        self._queue_api.update_provider_instance_settings(
            ctx.tenant, ctx.state.provider_instance, ctx.queue
        )

    def verify_queue_added(self, ctx: QueueExecutionContext):
        self.logging(
            f"Checking Queue: {ctx.queue.queue_name} exists for: {ctx.provider_instance}",
            "INFO",
        )

        instance = self._queue_api.get_provider_instance(
            ctx.tenant, ctx.state.provider_instance
        )

        queue_added = [
            queue
            for queue in instance.queue_list
            if queue.queue_name == ctx.queue.queue_name
        ]
        if queue_added:
            self.logging(
                f"Found Queue: {ctx.queue.queue_name} exists for: {ctx.provider_instance}",
                "INFO",
            )
        else:
            raise QueueNotFound

    def check_duplicate_queue(self, ctx: QueueExecutionContext):
        self.logging(
            f"Checking Queue: {ctx.queue.queue_name} exists for: {ctx.provider_instance}",
            "INFO",
        )

        instance = self._queue_api.get_provider_instance(
            ctx.tenant, ctx.state.provider_instance
        )

        queue_added = [
            queue
            for queue in instance.queue_list
            if queue.queue_name == ctx.queue.queue_name
        ]
        if queue_added:
            raise DuplicateNameException

    def execute(self) -> QueueExecutionResult:
        """
        Executes the queue creation process by navigating through the form pages and submitting queues.
        """

        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )

            if not self._is_provider_settings_usable(self._ctx):
                self.logging(
                    "Provider Settings Not cached in state. Getting Provider Settings.",
                    "INFO",
                )
                for step in self._ensure_form_flow:
                    self.run_step(step)

            self.logging("Provider Settings cached in state. Continuing", "INFO")
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

        except NotAuthenticatedException:
            return self._build_error_result(
                status=QUEUEEXECSTATUS.NOT_AUTHENTICATED,
                message="Received Not Autenticated Response from Server.",
            )
        except RetryableNetworkException:
            return self._build_error_result(
                status=QUEUEEXECSTATUS.NETWORK_RETRYABLE_ERROR,
                message="Received an Network Retryable Error from the server.",
            )
        except NetworkResponseException:
            return self._build_error_result(
                status=QUEUEEXECSTATUS.NETWORK_RESPONSE_ERROR,
                message="Received a Network Response Error.",
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
    # ENSURE PROVIDER SETTINGS

    def find_provider_name(self, ctx: QueueExecutionContext):
        self.logging(f"Trying to Find Provider Name: {ctx.provider_name}", "INFO")
        providers = self._queue_api.get_providers(ctx.tenant)
        is_provider = [
            provider
            for provider in providers
            if provider.name.lower() == ctx.provider_name.lower()
        ]

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

        is_instance = [
            instance
            for instance in instances
            if instance.name.lower() == ctx.provider_instance.lower()
        ]

        if is_instance:
            ctx.state.provider_instance = is_instance[0]
            self.logging(f"Found Provider Instance: {ctx.provider_instance}", "INFO")
        else:
            raise ProviderInstanceNotFound(
                f"Provider Instance Name: {ctx.provider_instance} does not exist."
            )

    def find_queue_custom_resource(self, ctx: QueueExecutionContext):
        self.logging(f"Trying to Find Custom Resources: {ctx.provider_name}", "INFO")

        resources = self._queue_api.get_custom_resources(
            ctx.tenant, ctx.state.provider_info
        )

        is_queue_resource = [
            resource
            for resource in resources
            if resource.name == "queue"
            and resource.providerDefinitionId == ctx.state.provider_info.id
        ]

        if is_queue_resource:
            ctx.state.queue_custom_resource = is_queue_resource[0]
            self.logging(
                f"Found Custom Resource for Provider: {ctx.provider_name}", "INFO"
            )
        else:
            raise ProviderInstanceNotFound(
                f"Custom Resources For Provider Name: {ctx.provider_name} does not exist."
            )
