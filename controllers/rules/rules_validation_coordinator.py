from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation import ValidationService
    from services.base.models import JobResponse
    from services.validation.models import ValidationResponse, SchemaValidateResponse
    from services.logger.adapters import LogAdapter

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


from services.rule_runner.models import (
    RuleRunnerRequestPayload,
)
from .models import ValidationBatch
from .enums import VALIDATIONBATCHTYPE
from base import ControllerBase


class RulesValidationCoordinator(ControllerBase):
    batch_complete = Signal(object)

    def __init__(self, logger: LogAdapter, validation_service: ValidationService):
        super().__init__(logger)
        self.validation_service = validation_service

        self._active_jobs: dict[str, SchemaValidatePayload] = {}
        self._active_batches: dict[str, ValidationBatch] = {}
        self._active_runners: dict[str, RuleRunnerRequestPayload] = {}
        # CONNECTIONS
        self.validation_service.task_complete.connect(self.on_validation_complete)

    def validate_rules(
        self, data, batch_type: VALIDATIONBATCHTYPE, file_path: str = ""
    ):
        rules = data.get("rules") or []
        batch_id = str(uuid4())
        rule_batch_name = data.get("rule_set_name", f"Rule Batch - {batch_id}")
        rule_batch_description = data.get("description", "")
        batch = ValidationBatch(
            batch_type=batch_type,
            rule_batch_name=rule_batch_name,
            rule_batch_description=rule_batch_description,
            batch_id=batch_id,
            batch_total=len(rules),
            file_path=file_path,
        )
        self._active_batches[batch_id] = batch
        if not rules and batch_type == VALIDATIONBATCHTYPE.SYS_SAVE:
            self._finalize_batch(batch.batch_id)
            return

        for rule in rules:
            rule_guid = rule.get("guid", None)
            if not rule_guid:
                rule_guid = str(uuid4())
                rule["guid"] = rule_guid
            payload = SchemaValidatePayload(schema_type=SCHEMATYPE.RULES, data=rule)
            job = JobRequest(
                id=batch_id,
                task=None,
                payload=ValidationRequest(kind=VALIDATEJOBTYPE.SCHEMA, data=payload),
            )
            self._active_jobs[rule_guid] = rule
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
        rule_guid = payload.guid

        batch = self._active_batches.get(job_id)
        data = self._active_jobs.get(rule_guid)
        if not data:
            return

        rule_name = data.get("rule_name")
        if not rule_name:
            rule_name = "Rule Has No Name"

        if is_valid:
            batch.valid_rules.append(data)
            batch.validation_total += 1
            self._logging(f"{rule_name}: 0 errors found.", LOGLEVEL.INFO)
        else:
            batch.invalid_rules.append(data)
            batch.validation_total += 1
            batch.total_errors += 1
            batch.rule_errors.extend(errors)
            self._logging(
                f"{rule_name}: {total_errors} errors found in rule.", LOGLEVEL.ERROR
            )

        self._active_jobs.pop(rule_guid)
        if batch.batch_total == batch.validation_total:
            self._finalize_batch(job_id)

    def _finalize_batch(self, batch_id: str):
        batch = self._active_batches.pop(batch_id)
        self.batch_complete.emit(batch)
