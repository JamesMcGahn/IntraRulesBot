from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation import ValidationService
    from services.base.models import JobResponse
    from services.validation.models import ValidationResponse, SchemaValidateResponse
    from services.rules import RuleRegistry, RuleStore, RuleBuilder
    from services.validation.models import SchemaError
    from services.rule_runner import RuleRunnerService
    from services.rule_runner.interfaces import RuleRunnerConfigProvider

from uuid import uuid4
from pathlib import Path
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
from services.rule_runner.models import (
    RuleRunnerResponse,
    RuleRunnerRequestPayload,
    RuleRunItem,
)
from services.rules.models import RuleSet
from .models import ValidationBatch, ValidationRulesResult
from .enums import VALIDATIONBATCHTYPE
from utils.files import PathManager


class RulesController(QObjectBase):
    ui_event = Signal(object)
    runtime_validation_result = Signal(object)
    # TODO convert to ui_event
    runner_progress = Signal(int, int)
    stop_runner_service = Signal()

    def __init__(
        self,
        validation_service: ValidationService,
        rules_registry: RuleRegistry,
        rule_builder: RuleBuilder,
        rule_store: RuleStore,
        rule_runner_service: RuleRunnerService,
        settings_provider: RuleRunnerConfigProvider,
    ):
        super().__init__()
        self.validation_service = validation_service
        self.rules_registry = rules_registry
        self.rule_builder = rule_builder
        self.rules_store = rule_store
        self.rule_runner_service = rule_runner_service
        self._settings_provider = settings_provider

        self._active_jobs: dict[str, SchemaValidatePayload] = {}
        self._active_batches: dict[str, ValidationBatch] = {}
        self._active_runners: dict[str, RuleRunnerRequestPayload] = {}
        # CONNECTIONS
        self.validation_service.task_complete.connect(self.on_validation_complete)
        # TODO convert to ui_event
        self.rule_runner_service.progress.connect(self.runner_progress)
        self.stop_runner_service.connect(self.rule_runner_service.stop_current_run)

    def hydrate_rules_page(self):
        self._emit_rules_updated()

    def load_editor_state(self):
        path = PathManager.create_folder_in_app_data("rule_editor_state")
        base_dir = Path(path)
        file_path = base_dir / "rule_editor_state.json"
        data, error = self.rules_store.load_from_json(file_path=file_path)
        if not data:
            return

        raw_rules = data.get("rules", None)
        raw_rule_set = data
        if not raw_rules:
            return

        import_rules = self.rule_builder.build_rules(raw_rules)
        import_rule_set = RuleSet(
            rule_set_name=raw_rule_set.get("rule_set_name", "Editor Rules"),
            description=raw_rule_set.get("description", "Editor Saved State"),
            guid=str(uuid4()),
            rules_guids=[rule.guid for rule in import_rules],
        )
        self.rules_registry.add_rules(import_rules)
        self.rules_registry.add_rule_set(import_rule_set)

    # FEATURE Add an Import File Type - Right now active guids will overwrite.
    def import_from_file(self, file_path):
        self.logging(f"Opening file - {file_path} to load json data.", LOGLEVEL.INFO)
        data, error = self.rules_store.load_from_json(file_path=file_path)

        if error:
            self.send_toast_failure(title="Error Loading File", message=error)
            return

        if not data.get("rules"):
            message = f"Error in the file {file_path} - File has no data."
            self.send_toast_failure(title="Error Loading File", message=message)
            return

        self.validate_json(data, VALIDATIONBATCHTYPE.IMPORT)

    def validate_json(self, data, batch_type: VALIDATIONBATCHTYPE, file_path: str = ""):
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
            file_path=file_path,
        )
        if not rules and batch_type == VALIDATIONBATCHTYPE.SYS_SAVE:
            self.handle_sys_save(batch)
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
            errors_grouped_dict = self._group_batch_errors(batch)

            self.runtime_validation_result.emit(
                ValidationRulesResult(errors_grouped_dict)
            )
        elif batch.batch_type == VALIDATIONBATCHTYPE.USER_SAVE:
            if batch.rule_errors:
                errors_grouped_dict = self._group_batch_errors(batch)

                self.runtime_validation_result.emit(
                    ValidationRulesResult(errors_grouped_dict)
                )
            else:
                if not batch.file_path:
                    return
                path = PathManager.regex_path(batch.file_path)
                rules = {
                    "rule_set_name": path["filename"],
                    "description": "Saved Rules From Editor",
                    "rules": batch.valid_rules,
                }

                is_saved, error = self.rules_store.save(rules, batch.file_path)
                if is_saved:
                    toast = ToastEvent(
                        message="File Saved",
                        title=f"File Saved to {batch.file_path}",
                        toast_level=QTOASTSTATUS.SUCCESS,
                        log_level=LOGLEVEL.INFO,
                    )
                    event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
                    self.ui_event.emit(event)
        elif batch.batch_type == VALIDATIONBATCHTYPE.SYS_SAVE:
            self.handle_sys_save(batch)

        elif batch.batch_type == VALIDATIONBATCHTYPE.RULE_RUNNER:
            self.handle_run_rules(batch)

    def handle_run_rules(self, batch: ValidationBatch):
        rules = self.rule_builder.build_rules(batch.valid_rules)
        rule_items = [RuleRunItem(rule.guid, rule) for rule in rules]
        login_config = self._settings_provider.get_rule_run_config()
        payload = RuleRunnerRequestPayload(login_config, rule_items)
        job_ref_id = uuid4()
        self._active_runners[job_ref_id] = RuleRunnerRequestPayload
        self.rule_runner_service.start_run(JobRequest(job_ref_id, None, payload))

    def handle_sys_save(self, batch: ValidationBatch):
        if batch.rule_errors:
            errors_grouped_dict = self._group_batch_errors(batch)

            self.runtime_validation_result.emit(
                ValidationRulesResult(errors_grouped_dict)
            )
        else:
            path = PathManager.create_folder_in_app_data("rule_editor_state")
            rules = {
                "rule_set_name": "Saved Rules",
                "description": "Saved Rules From Editor",
                "rules": batch.valid_rules,
            }
            base_dir = Path(path)
            file_path = base_dir / "rule_editor_state.json"
            is_saved, error = self.rules_store.save(rules, file_path)
            if is_saved:
                toast = ToastEvent(
                    message="Rules Saved",
                    title="Rules Saved to System",
                    toast_level=QTOASTSTATUS.SUCCESS,
                    log_level=LOGLEVEL.INFO,
                )
                event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
                self.ui_event.emit(event)

    def _group_batch_errors(
        self, batch: ValidationBatch
    ) -> dict[str, list[SchemaError]]:
        errors_grouped_dict: dict[str, list[SchemaError]] = {}

        for error in batch.rule_errors:
            if error.rule_guid not in errors_grouped_dict:
                errors_grouped_dict[error.rule_guid] = []
            errors_grouped_dict[error.rule_guid].append(error)
        for valid in batch.valid_rules:
            errors_grouped_dict[valid["guid"]] = []
        return errors_grouped_dict

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

    def handle_stop_runner(self):
        self.stop_runner_service.emit()
