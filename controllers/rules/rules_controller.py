from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rules_validation_coordinator import RulesValidationCoordinator
    from services.rules import RuleRegistry, RuleStore, RuleBuilder
    from services.validation.models import SchemaError
    from services.rule_runner import RuleRunnerService
    from services.rule_runner.interfaces import RuleRunnerConfigProvider
    from services.rule_sets.models import RuleSet
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from PySide6.QtCore import Signal, Slot
from copy import deepcopy
from base import QObjectBase
from base.enums import UIEVENTTYPE, LOGLEVEL
from base.events import ToastEvent, UIEvent, SchemaErrorDialogEvent, RulesLoadedEvent
from views.components.toasts.qtoast.enums import QTOASTSTATUS
from services.base.models import JobRequest

# TODO Create Rule Runner Response
from services.rule_runner.models import (
    RuleRunnerRequestPayload,
    RuleRunItem,
)
from .models import ValidationBatch, ValidationRulesResult
from .enums import VALIDATIONBATCHTYPE
from utils.files import PathManager


class RulesController(QObjectBase):
    ui_event = Signal(object)
    display_validation_result = Signal(object)
    rule_set_bookmarked = Signal(object)
    # TODO convert to ui_event
    runner_progress = Signal(int, int)
    stop_runner_service = Signal()

    def __init__(
        self,
        validation_coordinator: RulesValidationCoordinator,
        rules_registry: RuleRegistry,
        rule_builder: RuleBuilder,
        rule_store: RuleStore,
        rule_runner_service: RuleRunnerService,
        settings_provider: RuleRunnerConfigProvider,
    ):
        super().__init__()
        self.validation_coordinator = validation_coordinator
        self.rules_registry = rules_registry
        self.rule_builder = rule_builder
        self.rules_store = rule_store
        self.rule_runner_service = rule_runner_service
        self._settings_provider = settings_provider

        self._active_runners: dict[str, RuleRunnerRequestPayload] = {}
        # CONNECTIONS

        # TODO convert to ui_event
        self.rule_runner_service.progress.connect(self.runner_progress)
        self.stop_runner_service.connect(self.rule_runner_service.stop_current_run)
        ## RULES
        self.validation_coordinator.batch_complete.connect(self.on_validation_complete)
        self.batch_dispatchers = {
            VALIDATIONBATCHTYPE.IMPORT: self._handle_import_batch,
            VALIDATIONBATCHTYPE.RUNTIME: self._handle_run_time,
            VALIDATIONBATCHTYPE.USER_SAVE: self._handle_user_save,
            VALIDATIONBATCHTYPE.SYS_SAVE: self._handle_sys_save,
            VALIDATIONBATCHTYPE.RULE_RUNNER: self._handle_run_rules,
            VALIDATIONBATCHTYPE.BOOKMARK: self._handle_bookmark,
        }

    @Slot(object)
    def load_from_bookmarks(self, rule_set: RuleSet):
        rules = rule_set.rules
        new_rules = []
        for rule in rules:
            rule.guid = str(uuid4())
            new_rules.append(rule)
        self.rules_registry.add_rules(new_rules)
        self._emit_rules_updated()

    # **********************************
    # TOP NAV ACTIONS
    # FEATURE Add an Import File Type - Right now active guids will overwrite.
    def import_from_file(self, file_path: str):
        self.logging(f"Opening file - {file_path} to load json data.", LOGLEVEL.INFO)
        data, error = self.rules_store.load_from_json(file_path=file_path)

        if error:
            self.send_toast_failure(title="Error Loading File", message=error)
            return

        if not data.get("rules"):
            message = f"Error in the file {file_path} - File has no data."
            self.send_toast_failure(title="Error Loading File", message=message)
            return

        self.validate_rules(data, VALIDATIONBATCHTYPE.IMPORT)

    # **********************************
    # RULE PAGE ACTIONS

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
        if not raw_rules:
            return

        import_rules = self.rule_builder.build_rules(raw_rules)
        self.rules_registry.add_rules(import_rules)

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

    def validate_rules(
        self, data, batch_type: VALIDATIONBATCHTYPE, file_path: str = ""
    ):
        self.validation_coordinator.validate_rules(data, batch_type, file_path)

    def handle_user_book_mark(
        self, rule_set_name: str, rule_set_desc: str, rules: dict
    ):
        user_set_name = rule_set_name

        if not rule_set_name:
            today_date_text = datetime.now().strftime("%Y-%m-%d::%I:%M:%S %p")
            user_set_name = f"User Saved - {today_date_text}"

        data = {
            "rule_set_name": user_set_name,
            "description": rule_set_desc,
            "default": False,
            **rules,
        }
        self.validate_rules(data, VALIDATIONBATCHTYPE.BOOKMARK)

    def handle_stop_runner(self):
        self.stop_runner_service.emit()

    def on_validation_complete(self, batch: ValidationBatch):
        dispatcher = self.batch_dispatchers.get(batch.batch_type)

        if dispatcher is None:
            msg = f"{batch.batch_type} doesnt have a handler implemented"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)

        dispatcher(batch)

    # **********************************
    # VALIDATION HANDLERS

    def _handle_run_time(self, batch: ValidationBatch):
        self._display_validation(batch, "Validation")

    def _handle_bookmark(self, batch: ValidationBatch):
        self._display_validation(batch, "Bookmark Saved")
        if batch.rule_errors:
            return
        data = {
            "rule_set_name": batch.rule_batch_name,
            "description": batch.rule_batch_description,
            "default": False,
            "rules": batch.valid_rules,
        }
        self.rule_set_bookmarked.emit(data)

    def _handle_import_batch(self, batch: ValidationBatch):
        self._display_validation(batch, "Import")
        if batch.rule_errors:
            return
        rules = self.rule_builder.build_rules(batch.valid_rules)
        self.rules_registry.add_rules(rules)
        self._emit_rules_updated()

    def _handle_user_save(self, batch: ValidationBatch):
        self._display_validation(batch, "Saved")
        if batch.rule_errors:
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

    def _handle_run_rules(self, batch: ValidationBatch):
        self._display_validation(batch, "Run Rules")
        if batch.rule_errors:
            return
        rules = self.rule_builder.build_rules(batch.valid_rules)
        rule_items = [RuleRunItem(rule.guid, rule) for rule in rules]
        login_config = self._settings_provider.get_rule_run_config()
        if not login_config.login_valid:
            self.send_toast_failure(
                "Login Settings Not Valid",
                "Please validate all of the login settings on the Settings Page.",
            )
            return
        payload = RuleRunnerRequestPayload(login_config, rule_items)
        job_ref_id = str(uuid4())
        self._active_runners[job_ref_id] = payload
        self.rule_runner_service.start_run(JobRequest(job_ref_id, None, payload))

    def _handle_sys_save(self, batch: ValidationBatch):
        self._display_validation(batch, "Save Rules")
        if batch.rule_errors:
            return

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

    # **********************************
    # HELPERS

    def _display_validation(self, batch: ValidationBatch, type_name: str):
        errors_grouped_dict = self._group_batch_errors(batch)
        if batch.rule_errors:
            self._handle_batch_errors(type_name, batch)
        else:
            message = f"{type_name} Suceeded. 0 errors found in rule set."
            title = f"{type_name} Suceeded"
            self.send_toast_success(title, message)

        self.display_validation_result.emit(ValidationRulesResult(errors_grouped_dict))

    def _handle_batch_errors(self, batch_type: str, batch: ValidationBatch):
        message = f"""{batch_type} Failed. {batch.total_errors} errors found in rule set. View Errors Dialog for more details"""
        title = f"{batch_type} Failed"
        error = SchemaErrorDialogEvent(errors=batch.rule_errors)
        error_event = UIEvent(UIEVENTTYPE.DISPLAY, payload=error)
        self.send_toast_failure(title=title, message=message)
        self.ui_event.emit(error_event)

    def send_toast_failure(self, title, message):
        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=QTOASTSTATUS.SUCCESS,
            log_level=LOGLEVEL.INFO,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)

    def send_toast_success(self, title, message):
        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=QTOASTSTATUS.ERROR,
            log_level=LOGLEVEL.ERROR,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)

    def _emit_rules_updated(self):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=RulesLoadedEvent(rules=self.rules_registry.get_all()),
            )
        )

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
