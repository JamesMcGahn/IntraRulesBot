from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import RulesPageControllers
    from base.events import UIEvent

import uuid

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QFileDialog

from base import QWidgetBase
from base.events import (
    MonitorRowUpsertEvent,
    MonitorSummaryUpdateEvent,
    RulesLoadedEvent,
    RuleRunnerStateEvent,
)
from controllers.rules.enums import VALIDATIONBATCHTYPE
from views.components.dialogs import RuleSetDialog, SchemaErrorDialog
from views.components.toasts.qtoast.enums import QTOASTSTATUS

from .rules_monitor.rule_runner_monitor import RuleRunnerMonitor
from .rules_page_css import STYLES
from .rules_page_ui import RulesPageView


class RulesPage(QWidgetBase):
    """
    A controller class for managing the Rules page.
    Rules page is responsible for managing the rules displayed in the UI. It handles
    loading, validating, saving, and copying rule fields. The UI interactions are handled
    through the connected view and model components.
    """

    send_rules = Signal(list)
    send_rule_sets = Signal(object)
    display_validation_result = Signal(object)
    monitor_upsert_row = Signal(object)
    monitor_summary_update = Signal(object)
    progress_bar_update = Signal(int, int)
    rule_runner_state_update = Signal(object)

    def __init__(self, controllers: RulesPageControllers):
        """
        Initialize the RulesPage, set up models, connect signals/slots, and load the saved rules.
        """
        super().__init__()
        self.controllers = controllers
        self.rules_controller = controllers.rules
        self.monitor_controller = controllers.monitor
        self.setStyleSheet(STYLES)

        self.ui = RulesPageView()
        self.layout.addWidget(self.ui)

        self.forms_errors = []
        self.total_errors = 0
        self.rule_set_data = None
        self.setGraphicsEffect(None)

        ##
        self.rules_controller.ui_event.connect(self.receive_ui_event)
        self.monitor_controller.ui_event.connect(self.receive_ui_event)
        self.rules_controller.display_validation_result.connect(
            self.ui.update_form_validation
        )
        self.progress_bar_update.connect(self.ui.set_progress_bar)
        self.ui.delete_rule.connect(self.handle_delete_rule)
        self.ui.delete_all_rules.connect(self.handle_delete_all_rules)
        self.ui.clone_rule.connect(self.handle_clone_rule)
        self.ui.bookmark_rules.connect(self.handle_bookmark_rules)

        # Signal / Slot Connections
        self.ui.user_save_rules.connect(self.handle_user_rules_save)
        self.ui.validate_rules.connect(self.handle_validate_rules)
        self.ui.sys_save_rules.connect(self.handle_sys_rules_save)
        self.ui.start_runner.connect(self.handle_start_runner)
        self.ui.stop_runner.connect(self.handle_stop_runner)
        self.ui.display_monitor.connect(self.handle_display_monitor)
        self.send_rules.connect(self.ui.rules_changed)
        self.ui.validate_open_dialog.clicked.connect(self.display_errors_dialog)
        self.rule_runner_state_update.connect(self.ui.handle_rule_runner_state_update)

        self.dialog = RuleSetDialog()
        self.dialog.send_form.connect(self.save_rule_set)
        self.check_for_saved_rules()

        self.rule_runner_monitor = RuleRunnerMonitor(self)
        self.monitor_upsert_row.connect(self.rule_runner_monitor.handle_upsert_row)
        self.monitor_summary_update.connect(
            self.rule_runner_monitor.handle_summary_update
        )
        self.focus_object_name = None
        self.focus_object_text = None

    @Slot()
    def handle_display_monitor(self):
        if self.rule_runner_monitor and self.rule_runner_monitor.isVisible():
            self.rule_runner_monitor.close()
            return
        if self.rule_runner_monitor and not self.rule_runner_monitor.isVisible():
            self.rule_runner_monitor.show()
            return

    @Slot(object)
    def receive_ui_event(self, event: UIEvent):
        if isinstance(event.payload, RulesLoadedEvent):
            self.ui.rules_changed(event.payload.rules)
        elif isinstance(event.payload, MonitorRowUpsertEvent):
            self.monitor_upsert_row.emit(event.payload.row)
        elif isinstance(event.payload, MonitorSummaryUpdateEvent):
            self.progress_bar_update.emit(
                event.payload.summary.completed, event.payload.summary.total
            )
            self.monitor_summary_update.emit(event.payload.summary)
        elif isinstance(event.payload, RuleRunnerStateEvent):
            self.rule_runner_state_update.emit(event.payload.state)

    @Slot(str)
    def handle_delete_rule(self, guid: str):
        self.rules_controller.delete_rule(guid)

    @Slot(str)
    def handle_delete_all_rules(self):
        self.rules_controller.delete_all_rules()

    @Slot(str)
    def handle_clone_rule(self, guid: str):
        self.rules_controller.clone_rule(guid)

    @Slot(list)
    def handle_validate_rules(self, rules: dict):
        self.controllers.rules.validate_rules(
            rules, batch_type=VALIDATIONBATCHTYPE.RUNTIME
        )

    @Slot(list)
    def handle_start_runner(self, rules: dict):
        self.controllers.rules.validate_rules(
            rules, batch_type=VALIDATIONBATCHTYPE.RULE_RUNNER
        )

    @Slot(list)
    def handle_bookmark_rules(
        self, rule_set_name: str, rule_set_desc: str, rules: dict
    ):
        self.controllers.rules.handle_user_book_mark(
            rule_set_name, rule_set_desc, rules
        )

    def handle_stop_runner(self):
        self.log_with_toast(
            "Stop Runner Requested",
            "Stopping Rule Runner.",
            "INFO",
            QTOASTSTATUS.WARNING,
        )
        self.controllers.rules.handle_stop_runner()

    def display_errors_dialog(self) -> None:
        """
        Display the error dialog if validation errors are found in the form fields.
        """
        add = SchemaErrorDialog(self.forms_errors)
        self.ui.set_hidden_errors_dialog_btn(False)
        add.show()

    def check_for_saved_rules(self) -> None:
        """
        Check if there are any saved rules and emit them to the view.
        """
        self.rules_controller.hydrate_rules_page()

    def handle_user_rules_save(self, rules) -> None:
        """
        Save the validated rules to a JSON file selected by the user. It ensures the file has
        a `.json` extension.
        """
        if not rules:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return
        if file_path:
            # Ensure the file has a .json extension
            if not file_path.endswith(".json"):
                file_path += ".json"
        self.controllers.rules.validate_rules(
            rules, batch_type=VALIDATIONBATCHTYPE.USER_SAVE, file_path=file_path
        )

    def handle_sys_rules_save(self, rules) -> None:
        """
        Save the validated rules to the internal system storage.
        """
        self.controllers.rules.validate_rules(
            rules, batch_type=VALIDATIONBATCHTYPE.SYS_SAVE
        )

    def on_bookmark_click(self):
        if self.ui.get_forms():
            _, data = self.validate_rules()
            if data:
                self.rule_set_data = data
                if not self.dialog.show():
                    self.rule_set_data = None

    @Slot(str, str)
    def save_rule_set(self, rule_set_name, rule_set_desc):
        rule_set = {
            "guid": str(uuid.uuid4()),
            "name": rule_set_name,
            "description": rule_set_desc,
            "rules": self.rule_set_data,
        }
        self.send_rule_sets.emit(rule_set)
        self.rule_set_data = None
        self.log_with_toast(
            "Rules Set Saved",
            f"Rules Set: {rule_set_name} Saved Successfully.",
            "INFO",
            "SUCCESS",
            True,
            self,
        )
