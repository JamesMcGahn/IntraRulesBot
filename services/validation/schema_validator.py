from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..base.models import JobRequest
    from .models import ValidationRequest, SchemaValidatePayload
    from jsonschema import ValidationError
    from services.logger.adapters import LogAdapter
    from .interfaces.schema_meta_provider import SchemaMetaProvider

from PySide6.QtCore import Signal

from .base_validator import BaseValidator
from ..base.enums import JOBSTATUS
from ..base.models import JobRef, JobResponse

from .enums import VALIDATEJOBTYPE
from .models import SchemaValidateResponse, ValidationResponse, SchemaError
from schemas.enums import SCHEMATYPE


class SchemaValidationService(BaseValidator):
    task_complete = Signal(object)

    def __init__(self, logger: LogAdapter, schema_meta_provider: SchemaMetaProvider):
        super().__init__(logger)
        self.schema_meta_provider = schema_meta_provider
        self._pending_jobs = {}

        self._schema_dispatcher = {
            SCHEMATYPE.RULES: self._validate_rules,
            SCHEMATYPE.QUEUES: self._validate_queues,
        }

    def validate(
        self, job: JobRequest[ValidationRequest[SchemaValidatePayload]]
    ) -> JobResponse[ValidationResponse]:
        self._pending_jobs[job.id] = job

        payload = job.payload.data

        dispatcher = self._schema_dispatcher.get(payload.schema_type, None)
        if dispatcher is None:
            msg = f"Validator for {payload.schema_type} has not been implemented."
            self._logging(msg, "ERROR")
            raise NotImplementedError(msg)

        dispatcher(job.id, payload)

    def _validate_queues(self, job_id: str, payload: SchemaValidatePayload):

        queue_guid = payload.data.get("guid")
        queue_name = payload.data.get("row_name")
        payload_errors = self._validate_payload(
            queue_name, queue_guid, SCHEMATYPE.QUEUES, payload.data
        )
        total_errors = len(payload_errors)
        valid = total_errors == 0
        result = SchemaValidateResponse(
            guid=queue_guid,
            schema_type=payload.schema_type,
            valid=valid,
            total_errors=total_errors,
            errors=payload_errors,
        )
        self.send_validation_response(job_id, result)

    def _validate_rules(self, job_id: str, payload: SchemaValidatePayload):
        rule_name = payload.data.get("rule_name")
        rule_guid = payload.data.get("guid")
        rule_name = rule_name or "Rule has no Name"
        payload_errors = self._validate_payload(
            rule_name, rule_guid, SCHEMATYPE.RULES, payload.data
        )
        total_errors = len(payload_errors)
        valid = total_errors == 0
        result = SchemaValidateResponse(
            guid=rule_guid,
            schema_type=payload.schema_type,
            valid=valid,
            total_errors=total_errors,
            errors=payload_errors,
        )
        self.send_validation_response(job_id, result)

    def _validate_payload(
        self, name: str, guid: str, schema_type: SCHEMATYPE, data: object
    ) -> list[SchemaError]:
        validator = self.schema_meta_provider.get_validator(schema_type)
        rule_errors = []
        for error in validator.iter_errors(data):
            failed_feild, error_path_msg, error_msg = self.format_validation_error(
                error
            )
            rule_errors.append(
                SchemaError(
                    name=name,
                    guid=guid,
                    message=error_msg,
                    error_path=error.path,
                    error_path_msg=error_path_msg,
                    failed_field=failed_feild,
                )
            )
        return rule_errors

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
