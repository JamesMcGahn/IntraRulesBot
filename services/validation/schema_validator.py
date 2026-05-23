from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..base.models import JobRequest
    from .models import ValidationRequest, SchemaValidatePayload
    from jsonschema import ValidationError

    from .interfaces.schema_meta_provider import SchemaMetaProvider

from PySide6.QtCore import Signal

from base import QObjectBase
from ..base.enums import JOBSTATUS
from ..base.models import JobRef, JobResponse

from .enums import VALIDATEJOBTYPE
from .models import SchemaValidateResponse, ValidationResponse, SchemaError


class SchemaValidationService(QObjectBase):
    task_complete = Signal(object)

    def __init__(self, schema_meta_provider: SchemaMetaProvider):
        super().__init__()
        self.schema_meta_provider = schema_meta_provider
        self._pending_jobs = {}

    def validate(
        self, job: JobRequest[ValidationRequest[SchemaValidatePayload]]
    ) -> JobResponse[ValidationResponse]:
        self._pending_jobs[job.id] = job

        payload = job.payload.data

        validator = self.schema_meta_provider.get_validator(payload.schema_type)

        rule_errors = []
        total_errors = 0
        rule_name = payload.data.get("rule_name")
        rule_guid = payload.data.get("guid")
        rule_name = rule_name or "Rule has no Name"
        for error in validator.iter_errors(payload.data):
            total_errors = total_errors + 1
            failed_feild, error_path_msg, error_msg = self.format_validation_error(
                error
            )
            rule_errors.append(
                SchemaError(
                    rule_name=rule_name,
                    rule_guid=rule_guid,
                    message=error_msg,
                    error_path=error.path,
                    error_path_msg=error_path_msg,
                    failed_field=failed_feild,
                )
            )

        valid = total_errors == 0
        result = SchemaValidateResponse(
            rule_guid=payload.data["guid"],
            schema_type=payload.schema_type,
            valid=valid,
            total_errors=total_errors,
            errors=rule_errors,
        )
        self.send_validation_response(job.id, result)

    def send_validation_response(self, job_id, res: SchemaValidateResponse):
        job = self._pending_jobs.get(job_id)
        if not job:
            return
        job_response = JobResponse(
            job_ref=JobRef(job_id, task=None, status=JOBSTATUS.COMPLETE),
            payload=ValidationResponse(kind=VALIDATEJOBTYPE.SCHEMA, data=res),
        )
        self.task_complete.emit(job_response)
        self._pending_jobs.pop(job_id)

    def format_validation_error(self, error: ValidationError) -> tuple[str, str, str]:
        """
        Formats a JSON schema validation error into a tuple containing the field that failed,
        the error path, and the error message.

        Args:
            error (ValidationError): The validation error to format.

        Returns:
            Tuple[str, str, str]: A tuple containing:
                - The failed field (str)
                - The error path message (str)
                - The error message (str)
        """
        error_message = (
            error.json_path.replace("$.", "")
            .replace("[", ".")
            .replace("]", "")
            .split(".")
        )
        failed_feild = error_message[-1]
        format_error = ""
        for i, error_part in enumerate(error_message):
            if i == 0 and error_part != "rules":
                break
            if i == 0:
                format_error = "There was an error in rules "
            elif error_part.isdigit():
                format_error += f"item number {int(error_part) +1} "
            else:
                format_error += f"- {error_part} "

        error_path_msg = format_error.strip() + "."

        return (failed_feild, error_path_msg, error.message)
