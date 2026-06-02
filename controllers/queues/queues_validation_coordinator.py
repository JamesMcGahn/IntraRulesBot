from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation import ValidationService
    from services.base.models import JobResponse
    from services.validation.models import ValidationResponse, SchemaValidateResponse
    from services.logger.adapters import LogAdapter
    from services.files.models import ImportedSheetsRow

from uuid import uuid4
from PySide6.QtCore import Signal, Slot
from base.enums import LOGLEVEL
from schemas.enums import SCHEMATYPE
from services.base.models import JobRequest
from services.validation.enums import VALIDATEJOBTYPE
from services.validation.models import (
    SchemaValidatePayload,
    ValidationRequest,
    ValidationResponse,
)


from .models import ValidationQueueBatch, ValidationQueues
from .enums import VALIDATIONBATCHTYPE
from base import ControllerBase
from pathlib import Path


class QueuesValidationCoordinator(ControllerBase):
    batch_complete = Signal(object)

    def __init__(self, logger: LogAdapter, validation_service: ValidationService):
        super().__init__(logger)
        self.validation_service = validation_service

        self._active_jobs: dict[str, ImportedSheetsRow] = {}
        self._active_batches: dict[str, ValidationQueueBatch] = {}
        # CONNECTIONS
        self.validation_service.task_complete.connect(self.on_validation_complete)

    def validate_queues(self, data: ValidationQueues, batch_type: VALIDATIONBATCHTYPE):
        file_name = Path(data.file_path).name
        batch_id = str(uuid4())
        batch = ValidationQueueBatch(
            provider_name=data.provider_name,
            provider_instance=data.provider_instance,
            batch_type=batch_type,
            batch_name=file_name,
            batch_id=batch_id,
            batch_total=len(data.rows),
            file_path=data.file_path,
        )
        self._active_batches[batch_id] = batch

        for queue in data.rows:
            queue_guid = str(uuid4())

            queue_row = {
                "guid": queue_guid,
                "row_name": f"Row {queue.row_number}",
                **queue.values,
            }
            payload = SchemaValidatePayload(
                schema_type=SCHEMATYPE.QUEUES, data=queue_row
            )
            job = JobRequest(
                id=batch_id,
                task=None,
                payload=ValidationRequest(kind=VALIDATEJOBTYPE.SCHEMA, data=payload),
            )
            self._active_jobs[queue_guid] = queue
            self.validation_service.validate(job)

    @Slot(object)
    def on_validation_complete(
        self, job_res: JobResponse[ValidationResponse[SchemaValidateResponse]]
    ):
        job_id = job_res.job_ref.id
        if job_id not in self._active_batches:
            return

        payload = job_res.payload.data
        total_errors = payload.total_errors
        errors = payload.errors
        is_valid = payload.valid
        queue_guid = payload.guid

        batch = self._active_batches.get(job_id)
        data = self._active_jobs.get(queue_guid)
        if not data:
            return

        if is_valid:
            batch.valid_queues.append(data)
            batch.validation_total += 1
            self._logging(f"Row {data.row_number}: 0 errors found.", LOGLEVEL.INFO)
        else:
            batch.invalid_queues.append(data)
            batch.validation_total += 1
            batch.total_errors += 1
            batch.errors.extend(errors)
            self._logging(
                f"Row {data.row_number}: {total_errors} errors found in queue.",
                LOGLEVEL.ERROR,
            )

        self._active_jobs.pop(queue_guid)
        if batch.batch_total == batch.validation_total:
            self._finalize_batch(job_id)

    def _finalize_batch(self, batch_id: str):
        batch = self._active_batches.pop(batch_id)
        self.batch_complete.emit(batch)
