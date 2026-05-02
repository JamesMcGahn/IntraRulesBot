from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation import ValidationService
    from services.base.models import JobResponse
    from services.validation.models import ValidationResponse, SchemaValidateResponse
    from services.rules import RuleRegistry
    from services.validation.models import SchemaError

from uuid import uuid4

from PySide6.QtCore import Signal, Slot
from copy import deepcopy
from base import QObjectBase
from base.enums import UIEVENTTYPE, LOGLEVEL
from base.events import ToastEvent, UIEvent, SchemaErrorDialogEvent, RulesLoadedEvent
from views.components.toasts.qtoast.enums import QTOASTSTATUS
from schemas.enums import SCHEMATYPE
from services.base.models import JobRequest
from services.validation.enums import VALIDATEJOBTYPE
from services.validation.models import (
    SchemaValidatePayload,
    ValidationRequest,
    ValidationResponse,
)
from services.rules.models import RuleSet
import json
from .models import ValidationBatch, ValidationRulesResult
from .enums import VALIDATIONBATCHTYPE
from services.rules.rule_builder import RuleBuilder


class RulesController(QObjectBase):
    ui_event = Signal(object)
    runtime_validation_result = Signal(object)

    def __init__(
        self, validation_service: ValidationService, rules_registry: RuleRegistry
    ):
        super().__init__()
        self.validation_service = validation_service
        self.rules_registry = rules_registry
        self.rule_builder = RuleBuilder()

        self._active_jobs: dict[str, SchemaValidatePayload] = {}
        self._active_batches: dict[str, ValidationBatch] = {}

        # CONNECTIONS
        self.validation_service.task_complete.connect(self.on_validation_complete)

    def import_from_file(self, file_path):
        self.logging(f"Opening file - {file_path} to load json data.", LOGLEVEL.INFO)
        data = None
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

        except json.JSONDecodeError as e:
            message = f"JSON error in the file {file_path} - {str(e)}"
            self.send_toast_failure(title="Error Loading File", message=message)
            return
        except Exception as e:
            message = f"Error in the file {file_path} - {str(e)}"
            self.send_toast_failure(title="Error Loading File", message=message)
            return

        if not data.get("rules"):
            message = f"Error in the file {file_path} - File has no data."
            self.send_toast_failure(title="Error Loading File", message=message)
            return

        self.validate_json(data, VALIDATIONBATCHTYPE.IMPORT)

    def validate_json(self, data, batch_type: VALIDATIONBATCHTYPE):
        rules = data.get("rules")
        batch_id = str(uuid4())
        rule_batch_name = data.get("rule_set_name", f"Rule Batch - {batch_id}")
        rule_batch_description = data.get("description", "")
        batch = ValidationBatch(
            batch_type=batch_type,
            rule_batch_name=rule_batch_name,
            rule_batch_description=rule_batch_description,
            batch_id=batch_id,
            batch_total=len(rules),
        )
        self._active_batches[batch_id] = batch
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
        rule_guid = payload.rule_guid

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
            self.logging(f"{rule_name}: 0 errors found.", LOGLEVEL.INFO)
        else:
            batch.invalid_rules.append(data)
            batch.validation_total += 1
            batch.total_errors += 1
            batch.rule_errors.extend(errors)
            self.logging(
                f"{rule_name}: {total_errors} errors found in rule.", LOGLEVEL.ERROR
            )

        self._active_jobs.pop(rule_guid)
        if batch.batch_total == batch.validation_total:
            self._finalize_batch(job_id)

    def _finalize_batch(self, batch_id: str):
        batch = self._active_batches.pop(batch_id)
        if batch.batch_type == VALIDATIONBATCHTYPE.IMPORT:
            if batch.rule_errors:
                message = f"""Import Failed. {batch.total_errors} errors found in rule set. View Errors Dialog for more details"""
                title = "Import Failed"
                error = SchemaErrorDialogEvent(errors=batch.rule_errors)
                error_event = UIEvent(UIEVENTTYPE.DISPLAY, payload=error)
                self.send_toast_failure(title=title, message=message)
                self.ui_event.emit(error_event)
            else:
                toast = ToastEvent(
                    message="Import Suceeded. 0 errors found in rule set.",
                    title="Import Suceeded",
                    toast_level=QTOASTSTATUS.SUCCESS,
                    log_level=LOGLEVEL.INFO,
                )
                event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
                self.ui_event.emit(event)

                rules = self.rule_builder.build_rules(batch.valid_rules)
                rule_set = RuleSet(
                    rule_set_name=batch.rule_batch_name,
                    description=batch.rule_batch_description,
                    guid=str(uuid4()),
                    rules_guids=[rule.guid for rule in rules],
                )
                self.rules_registry.add_rules(rules)
                self.rules_registry.add_rule_set(rule_set)
                self._emit_rules_updated()
        elif batch.batch_type == VALIDATIONBATCHTYPE.RUNTIME:
            errors_grouped_dict: dict[str, list[SchemaError]] = {}

            for error in batch.rule_errors:
                if error.rule_guid not in errors_grouped_dict:
                    errors_grouped_dict[error.rule_guid] = []
                errors_grouped_dict[error.rule_guid].append(error)
            for valid in batch.valid_rules:
                errors_grouped_dict[valid["guid"]] = []

            self.runtime_validation_result.emit(
                ValidationRulesResult(errors_grouped_dict)
            )

    def send_toast_failure(self, title, message):
        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=QTOASTSTATUS.ERROR,
            log_level=LOGLEVEL.ERROR,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)

    def delete_rule(self, rule_guid: str):
        self.rules_registry.delete(rule_guid)
        self._emit_rules_updated()

    def delete_all_rules(self):
        self.rules_registry.delete_all()
        self._emit_rules_updated()

    def clone_rule(self, rule_guid: str):
        rule = self.rules_registry.get(rule_guid)
        if not rule:
            return

        new_rule = deepcopy(rule)
        new_rule.guid = str(uuid4())

        self.rules_registry.upsert(new_rule)
        self._emit_rules_updated()

    def _emit_rules_updated(self):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=RulesLoadedEvent(rules=self.rules_registry.get_all()),
            )
        )
