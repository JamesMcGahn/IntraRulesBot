from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from services.files import SpreadsheetFileService
    from .models import SpreadSheetImport
    from .queues_validation_coordinator import QueuesValidationCoordinator
    from services.queues import QueueBuilder
    from services.settings.providers import SettingsQueueRunnerConfigProvider
    from services.queue_runner import QueueRunnerService
from base.enums import UIEVENTTYPE
from base.events import UIEvent, SchemaErrorDialogEvent
from services.queue_runner.models import QueueRunItem, QueueRunnerRequestPayload

from services.files.spreadsheet_file_service import SpreadsheetFileService
from base import ControllerBase
from .models import ValidationQueueBatch, ValidationQueues
from .enums import VALIDATIONBATCHTYPE
from uuid import uuid4
from services.base.models import JobRequest
from dataclasses import fields


class QueuesController(ControllerBase):

    def __init__(
        self,
        logger: LogAdapter,
        spread_sheet_service: SpreadsheetFileService,
        validation_coordinator: QueuesValidationCoordinator,
        queue_builder: QueueBuilder,
        queue_runner_service: QueueRunnerService,
        settings_provider: SettingsQueueRunnerConfigProvider,
    ):
        super().__init__(logger)
        self._spread_sheet_service = spread_sheet_service
        self._validation_coordinator = validation_coordinator
        self._queue_builder = queue_builder
        self._settings_provider = settings_provider
        self._queue_runner_service = queue_runner_service
        self._validation_coordinator.batch_complete.connect(self.on_validation_complete)
        self._active_runners: dict[str, QueueRunnerRequestPayload] = {}

    def import_file(self, action: SpreadSheetImport):
        if any(not getattr(action, field.name) for field in fields(action)):
            self.send_toast_failure(
                "Queue Form: All Fields Need a Value",
                "All fields need to be populated in the queues form before starting the Queue Runner.",
            )
            return
        import_res = self._spread_sheet_service.load(
            action.file_location,
            required_headers={"queue_name", "queue_number"},
        )
        if import_res.ok:
            self.send_toast_success("Queues Import Succeeded", import_res.message)
            validate_payload = ValidationQueues(
                provider_name=action.provider_name,
                provider_instance=action.provider_instance,
                file_path=import_res.file_path,
                rows=import_res.rows,
            )
            self._validation_coordinator.validate_queues(
                data=validate_payload, batch_type=VALIDATIONBATCHTYPE.QUEUE_RUNNER
            )
        else:
            self.send_toast_failure("Queues Import Failed", import_res.message)

    def on_validation_complete(self, batch: ValidationQueueBatch):
        print(batch)
        self._display_validation(batch, "Queue Import")
        if batch.errors:
            return

        queues = self._queue_builder.build_queues(batch.valid_queues)

        queue_items = [QueueRunItem(queue.guid, queue) for queue in queues]
        login_config = self._settings_provider.get_queue_run_config()
        if not login_config.login_valid:
            self.send_toast_failure(
                "Login Settings Not Valid",
                "Please validate all of the login settings on the Settings Page.",
            )
            return
        payload = QueueRunnerRequestPayload(
            config=login_config,
            queues=queue_items,
            provider_instance=batch.provider_instance,
            provider_name=batch.provider_name,
        )
        job_ref_id = str(uuid4())
        self._active_runners[job_ref_id] = payload
        self._queue_runner_service.start_run(JobRequest(job_ref_id, None, payload))

    def _display_validation(self, batch: ValidationQueueBatch, type_name: str):

        if batch.errors:
            self._handle_batch_errors(type_name, batch)
        else:
            message = f"{type_name} Suceeded. 0 errors found in queue set."
            title = f"{type_name} Suceeded"
            self.send_toast_success(title, message)

    def _handle_batch_errors(self, batch_type: str, batch: ValidationQueueBatch):
        message = f"""{batch_type} Failed. {batch.total_errors} errors found in queue set. View Errors Dialog for more details"""
        title = f"{batch_type} Failed"
        error = SchemaErrorDialogEvent(errors=batch.errors)
        error_event = UIEvent(UIEVENTTYPE.DISPLAY, payload=error)
        self.send_toast_failure(title=title, message=message)
        self.ui_event.emit(error_event)
