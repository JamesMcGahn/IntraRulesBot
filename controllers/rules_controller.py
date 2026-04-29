from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation import ValidationService
    from services.base.models import JobResponse
    from services.validation.models import ValidationResponse, SchemaValidateResponse


from uuid import uuid4

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from base.enums import UIEVENTTYPE
from services.base.enums import JOBSTATUS
from schemas.enums import SCHEMATYPE
from services.base.models import JobRequest
from services.validation.enums import VALIDATEJOBTYPE
from services.validation.models import (
    SchemaValidatePayload,
    ValidationRequest,
    ValidationResponse,
)
import json


class RulesController(QObjectBase):

    def __init__(
        self,
        validation_service: ValidationService,
    ):
        super().__init__()
        self.validation_service = validation_service
        self._active_jobs: dict[str, SchemaValidatePayload] = {}

        # CONNECTIONS
        self.validation_service.task_complete.connect(self.on_validation_complete)

    def import_from_file(self, file_path):
        self.logging(f"Opening file - {file_path} to load json data.", "INFO")
        data = None
        try:

            with open(file_path, "r") as file:
                data = json.load(file)
                data = data.get("rules", [])

        except json.JSONDecodeError as e:
            # TODO: Send Event to Display Error
            self.logging(f"JSON error in the file {file_path} - {str(e)}", "ERROR")
        except Exception as e:
            # TODO: Send Event to Display Error
            self.logging(f"Error in the file {file_path} - {str(e)}", "ERROR")

        if not data:
            pass
            # TODO: Send Event to Display
        self.validate_json(data)

    def validate_json(self, data: list[dict]):
        for rule in data:
            job_id = str(uuid4())
            payload = SchemaValidatePayload(schema_type=SCHEMATYPE.RULES, data=rule)
            job = JobRequest(
                id=job_id,
                task=None,
                payload=ValidationRequest(kind=VALIDATEJOBTYPE.SCHEMA, data=payload),
            )
            self._active_jobs[job_id] = payload
            self.validation_service.validate(job)

    @Slot(object)
    def on_validation_complete(
        self, job_res: JobResponse[ValidationResponse[SchemaValidateResponse]]
    ):
        job_id = job_res.job_ref.id
        if job_id not in self._active_jobs:
            return

        payload = job_res.payload.data
        total_errors = payload.total_errors
        errors = payload.errors
        is_valid = payload.valid

        data = self._active_jobs.get(job_id).data
        rule_name = data.get("rule_name")

        if not rule_name:
            rule_name = "Rule Has No Name"

        if not is_valid:
            self.logging(
                f"{rule_name}: {total_errors} errors found in rule. Skipping Rule",
                "ERROR",
            )
            # TODO Display ERROR
            return
        data["guid"] = job_id
        self.logging(
            f"{rule_name}: 0 errors found in . Sending Data to Rules Model", "INFO"
        )
        # TODO: LOAD TO RULE REGISTRY
