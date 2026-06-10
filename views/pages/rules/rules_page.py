from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import RulesPageControllers
    from base.events import UIEvent


from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QFileDialog

from base import QWidgetBase
from base.events import (
    MonitorRowUpsertEvent,
    MonitorSummaryUpdateEvent,
    RulesLoadedEvent,
    RuleRunnerStateEvent,
    MonitorSnapShotEvent,
)
from controllers.rules.enums import VALIDATIONBATCHTYPE
from views.components.toasts.qtoast.enums import QTOASTSTATUS

from .rules_monitor.rule_runner_monitor import RuleRunnerMonitor
from .rules_page_css import STYLES
from .rules_page_ui import RulesPageView
from .enums import RULESPAGEEVENT
from .models import RulesPageAction
from ...base.enums import MONITOREVENT


class RulesPage(QWidgetBase):
    """
    A controller class for managing the Rules page.
    Rules page is responsible for managing the rules displayed in the UI. It handles
    loading, validating, saving, and copying rule fields. The UI interactions are handled
    through the connected view and model components.
    """

    send_rules = Signal(list)
    display_validation_result = Signal(object)
    monitor_upsert_row = Signal(object)
    monitor_summary_update = Signal(object)
    progress_bar_update = Signal(int, int)
    rule_runner_state_update = Signal(object)
    monitor_snapshot_update = Signal(object)

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
        self.setGraphicsEffect(None)

        self.focus_object_name = None
        self.focus_object_text = None

        self.rule_runner_monitor = RuleRunnerMonitor(self)

        # Signal / Slot Connections
        # Controllers connections
        self.rules_controller.ui_event.connect(self.receive_ui_event)
        self.monitor_controller.ui_event.connect(self.receive_ui_event)

        self.rules_controller.display_validation_result.connect(
            self.ui.update_form_validation
        )

        # UI Page connections
        self.ui.rules_page_action.connect(self.handle_rule_page_action)
        self.progress_bar_update.connect(self.ui.set_progress_bar)
        self.send_rules.connect(self.ui.rules_changed)
        self.rule_runner_state_update.connect(self.ui.handle_rule_runner_state_update)

        # Monitor connections
        self.monitor_upsert_row.connect(self.rule_runner_monitor.handle_upsert_row)
        self.monitor_summary_update.connect(
            self.rule_runner_monitor.handle_summary_update
        )
        self.monitor_snapshot_update.connect(
            self.rule_runner_monitor.update_from_snapshot
        )
        self.rule_runner_monitor.monitor_action.connect(self.handle_monitor_actions)

        self.check_for_saved_rules()

    def check_for_saved_rules(self) -> None:
        """
        Check if there are any saved rules and emit them to the view.
        """
        self.rules_controller.hydrate_rules_page()

    # External UI Events

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
        elif isinstance(event.payload, MonitorSnapShotEvent):
            self.monitor_snapshot_update.emit(event.payload)
        elif isinstance(event.payload, RuleRunnerStateEvent):
            self.rule_runner_state_update.emit(event.payload.state)

    def handle_monitor_actions(self, action: MONITOREVENT):
        if action == MONITOREVENT.MONITOR_CLEAR_ALL:
            self.monitor_controller.clear_all()
            return
        if action == MONITOREVENT.MONITOR_REMOVE_SUCCEED:
            self.monitor_controller.remove_succeed()

    # ***********************************
    # RULES PAGE - BUTTON ACTIONS

    @Slot(object)
    def handle_rule_page_action(self, action: RulesPageAction):
        action_handlers = {
            RULESPAGEEVENT.START_RUNNER: self._handle_send_validation,
            RULESPAGEEVENT.SYS_SAVE_RULES: self._handle_send_validation,
            RULESPAGEEVENT.VALIDATE_RULES: self._handle_send_validation,
            RULESPAGEEVENT.USER_SAVE_RULES: self._handle_user_rules_save,
            RULESPAGEEVENT.DELETE_ALL_RULES: self._handle_delete_all_rules,
            RULESPAGEEVENT.DELETE_RULE: self._handle_delete_rule,
            RULESPAGEEVENT.CLONE_RULE: self._handle_clone_rule,
            RULESPAGEEVENT.BOOKMARK_RULES: self._handle_bookmark_rules,
            RULESPAGEEVENT.STOP_RUNNER: self._handle_rule_runner_stop,
            RULESPAGEEVENT.TOGGLE_DISPLAY_MONITOR: self._handle_display_monitor,
        }

        handler = action_handlers.get(action.event, None)
        if handler is None:
            return
        handler(action)

    # ***********************************
    # RULE PAGE BUTTON ACTION - HANDLERS

    def _handle_rule_runner_stop(self, _) -> None:
        self.log_with_toast(
            "Stop Runner Requested",
            "Stopping Rule Runner.",
            "INFO",
            QTOASTSTATUS.WARNING,
        )
        self.controllers.rules.handle_stop_runner()

    def _handle_display_monitor(self, _) -> None:
        if self.rule_runner_monitor and self.rule_runner_monitor.isVisible():
            self.rule_runner_monitor.close()
            return
        if self.rule_runner_monitor and not self.rule_runner_monitor.isVisible():
            self.rule_runner_monitor.show()
            return

    def _handle_send_validation(self, action: RulesPageAction[dict]):
        batch_type_map = {
            RULESPAGEEVENT.VALIDATE_RULES: VALIDATIONBATCHTYPE.RUNTIME,
            RULESPAGEEVENT.START_RUNNER: VALIDATIONBATCHTYPE.RULE_RUNNER,
            RULESPAGEEVENT.SYS_SAVE_RULES: VALIDATIONBATCHTYPE.SYS_SAVE,
            RULESPAGEEVENT.USER_SAVE_RULES: VALIDATIONBATCHTYPE.USER_SAVE,
        }
        self.controllers.rules.validate_rules(
            action.data, batch_type=batch_type_map.get(action.event)
        )

    def _handle_bookmark_rules(self, action: RulesPageAction[object]) -> None:
        self.controllers.rules.handle_user_book_mark(
            action.data.get("rule_set_name"),
            action.data.get("rule_set_description"),
            action.data.get("rules"),
        )

    def _handle_clone_rule(self, action: RulesPageAction[str]) -> None:
        self.rules_controller.clone_rule(action.data)

    def _handle_delete_all_rules(self, _):
        self.rules_controller.delete_all_rules()

    def _handle_delete_rule(self, action: RulesPageAction[str]) -> None:
        self.rules_controller.delete_rule(action.data)

    def _handle_user_rules_save(self, action: RulesPageAction[dict]) -> None:
        """
        Save the validated rules to a JSON file selected by the user. It ensures the file has
        a `.json` extension.
        """
        if not action or not action.data:
            return
        rules = action.data
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return

        # Ensure the file has a .json extension
        if not file_path.endswith(".json"):
            file_path += ".json"
        self.controllers.rules.validate_rules(
            rules, batch_type=VALIDATIONBATCHTYPE.USER_SAVE, file_path=file_path
        )
