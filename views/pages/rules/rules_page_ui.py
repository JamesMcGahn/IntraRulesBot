from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.rules.models import ValidationRulesResult
    from services.rules.models import Rule

from typing import List

from PySide6.QtCore import QSize, Qt, Signal, Slot, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from views.components.buttons import EditorActionButton, GradientButton
from views.components.helpers import StyleHelper, WidgetFactory
from views.components.layouts import ScrollArea, StackedFormWidget

from ...components.dialogs import RuleSetDialog, SchemaErrorDialog
from ...components.rules import RuleAdapter, RuleEventFilter, RuleFactory
from ...components.rules.rule_registry import RuleFieldRegistry
from services.rule_runner.enums.rule_runner_lifecycle import RULERUNNERLIFECYCLE
from .enums.rules_page_event import RULESPAGEEVENT
from .models import RulesPageAction


class RulesPageView(QWidget):
    """
    A UI component that represents the Rules Page.
    This view includes buttons for navigating, adding, cloning, deleting, and saving rules,
    along with a validation feedback button and a progress bar for operations.
    """

    rules_form_updated = Signal()

    rules_page_action = Signal(object)

    def __init__(self):
        super().__init__()
        self.current_rule_index = 0
        self.event_filter = RuleEventFilter()
        self._event_guid = None
        self._event_path = None
        self.init_ui()

        self._form_errors = []

    def init_ui(self) -> None:
        """
        Sets up the UI layout and widgets for the rules page, including editor buttons,
        navigation buttons, and rule actions.
        """
        self.rule_set_dialog = RuleSetDialog(self)
        self.current_rule_index = 0
        self.previous_guid = None

        self.rules_layout = QVBoxLayout(self)

        self.outter_layout = WidgetFactory.create_form_box(
            "Rules",
            self.rules_layout,
            False,
            object_name="Rules-Information",
            title_color="#fcfcfc",
        )

        self.main_layout = QVBoxLayout()

        # Editor Widget
        self.editor_widget = QWidget()
        StyleHelper.drop_shadow(self.editor_widget)
        self.editor_layout = QVBoxLayout(self.editor_widget)

        # Editor - Top Button Bar
        self.top_button_bar_layout = QHBoxLayout()
        self.editor_layout.addLayout(self.top_button_bar_layout)

        # Editor - Top Button Bar - Validate Section
        h_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.validate_feedback = QPushButton()
        self.validate_open_dialog = GradientButton(
            "View Errors",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.validate_open_dialog.setMaximumWidth(100)
        self.top_button_bar_layout.addWidget(self.validate_feedback)
        self.top_button_bar_layout.addWidget(self.validate_open_dialog)
        self.validate_open_dialog.setObjectName("open-errors-btn")
        self.validate_open_dialog.setHidden(True)
        self.validate_feedback.setStyleSheet(
            "background-color: transparent; border: none; font-size: 13px; color: white;"
        )
        self.no_error_icon = QIcon()
        self.no_error_icon.addFile(
            ":/images/orange_check.png", QSize(50, 20), QIcon.Mode.Normal
        )
        self.error_icon = QIcon()
        self.error_icon.addFile(
            ":/images/red_xmark.png", QSize(50, 20), QIcon.Mode.Normal
        )
        self.top_button_bar_layout.addItem(h_spacer)

        # Editor - Top Button Bar - Navigation Layout
        nav_btn_layout = QHBoxLayout()
        nav_btn_layout.setSpacing(1)
        self.top_button_bar_layout.addLayout(nav_btn_layout)
        self.prev_button = QPushButton()
        self.next_button = QPushButton()
        self.prev_button.setFixedWidth(30)
        self.next_button.setFixedWidth(30)
        self.nav_label = QLabel()

        self.nav_label.setObjectName("nav-label")
        nav_btn_layout.addWidget(self.nav_label)

        nav_btn_layout.addWidget(self.prev_button)
        nav_btn_layout.addWidget(self.next_button)

        WidgetFactory.create_icon(
            self.prev_button,
            ":/images/left_arrow_on.png",
            50,
            20,
        )
        WidgetFactory.create_icon(
            self.next_button,
            ":/images/right_arrow_on.png",
            50,
            20,
        )

        # Main Section
        hlayout = QHBoxLayout()

        # Vertical Button Bar - Actions Layout
        actions_btn_widget = QWidget()
        hlayout.addWidget(actions_btn_widget)
        actions_btn_widget.setStyleSheet("padding: 0; ")
        actions_btn_widget.setObjectName("actions-btn-widget")
        form_actions_btn_layout = QVBoxLayout(actions_btn_widget)

        form_actions_btn_layout.setSpacing(1)

        actions_btn_widget_inner = QWidget()
        actions_btn_widget_inner.setStyleSheet(
            "border: 1px solid #f58220; border-radius: 3px;"
        )

        self.form_actions_btn_inner_layout = QVBoxLayout(actions_btn_widget_inner)
        self.setup_actions_buttons()

        form_actions_btn_layout.addWidget(actions_btn_widget_inner)
        v_spacer = QSpacerItem(20, 40, QSizePolicy.Fixed, QSizePolicy.Expanding)
        form_actions_btn_layout.addItem(v_spacer)

        # Editor - Rules
        self.stacked_widget = StackedFormWidget()
        self.stacked_widget.setObjectName("Rules-Stacked-Widget")
        self.stacked_widget.setContentsMargins(0, 0, 15, 10)

        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidget(self.stacked_widget)

        hlayout.addWidget(self.scroll_area)
        self.editor_layout.addLayout(hlayout)

        # self.editor_layout.addWidget(self.scroll_area)

        self.main_layout.addWidget(self.editor_widget)
        self.outter_layout.addRow(self.main_layout)

        self.init_thread_controls()

        # Signal / Slot Connections
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.repaint_shadow)
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.repaint_shadow)

        self.prev_button.clicked.connect(self.show_previous_rule)
        self.next_button.clicked.connect(self.show_next_rule)

        self.bookmark.clicked.connect(self.handle_action_button_click)
        self.copy_field.clicked.connect(self.handle_copy_fields)

        self.validate_open_dialog.clicked.connect(self.display_errors_dialog)

        self.delete_all.clicked.connect(self.handle_action_button_click)
        self.trash.clicked.connect(self.handle_action_button_click)
        self.clone.clicked.connect(self.handle_action_button_click)
        self.validate.clicked.connect(self.handle_action_button_click)
        self.download.clicked.connect(self.handle_action_button_click)
        self.save.clicked.connect(self.handle_action_button_click)
        self.start.clicked.connect(self.handle_action_button_click)
        self.stop.clicked.connect(self.handle_action_button_click)
        self.monitor.clicked.connect(self.handle_action_button_click)
        self.rule_set_dialog.send_form.connect(self.handle_bookmark_rules)
        self.event_filter.event_changed.connect(self.focus_changed)

        # Setup
        self.update_navigation_buttons()

    def setup_actions_buttons(self) -> None:
        """
        Sets up action buttons for rule management (e.g., add, save, delete).
        """

        self.form_actions_btn_inner_layout.setSpacing(0)
        self.form_actions_btn_inner_layout.setContentsMargins(0, 0, 0, 0)
        # self.add = EditorActionButton("")
        self.save = EditorActionButton("")
        self.download = EditorActionButton("")
        self.validate = EditorActionButton("")
        self.clone = EditorActionButton("")
        self.copy_field = EditorActionButton("")
        self.trash = EditorActionButton("")
        self.delete_all = EditorActionButton("")
        self.bookmark = EditorActionButton("")

        actionBtns = [
            (
                self.save,
                "Save",
                RULESPAGEEVENT.SYS_SAVE_RULES,
                ":/images/save_off_b.png",
                ":/images/save_on.png",
            ),
            (
                self.validate,
                "Validate Fields",
                RULESPAGEEVENT.VALIDATE_RULES,
                ":/images/validate_off_b.png",
                ":/images/validate_on.png",
            ),
            (
                self.clone,
                "Clone Rule",
                RULESPAGEEVENT.CLONE_RULE,
                ":/images/clone_off_b.png",
                ":/images/clone_on.png",
            ),
            (
                self.copy_field,
                "Apply Field Value Across Rules",
                RULESPAGEEVENT.COPY_RULE_FIELD,
                ":/images/copy_field_off_b.png",
                ":/images/copy_field_on.png",
            ),
            (
                self.trash,
                "Delete Rule",
                RULESPAGEEVENT.DELETE_RULE,
                ":/images/trash_off_b.png",
                ":/images/trash_on.png",
            ),
            (
                self.download,
                "Save to File",
                RULESPAGEEVENT.USER_SAVE_RULES,
                ":/images/download_off_b.png",
                ":/images/download_on.png",
            ),
            (
                self.delete_all,
                "Delete All Rules",
                RULESPAGEEVENT.DELETE_ALL_RULES,
                ":/images/delete_all_off_b.png",
                ":/images/delete_all_on.png",
            ),
            (
                self.bookmark,
                "Save Rules to Rule Sets",
                RULESPAGEEVENT.BOOKMARK_RULES,
                ":/images/bookmark_off_b.png",
                ":/images/bookmark_on.png",
            ),
        ]

        for index, btn in enumerate(actionBtns):
            btn_ref, tool_tip, object_name, image_loc1, image_loc2 = btn

            btn_ref.setFixedWidth(40)
            btn_ref.setProperty("page_action", object_name)
            style = ""
            if index == 0:
                style = "border-top-left-radius: 3px; border-top-right-radius: 3px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;"
            elif index == len(actionBtns) - 1:
                style = "border-top-left-radius: 0px; border-top-right-radius: 0px; border-bottom-left-radius: 3px; border-bottom-right-radius: 3px;"
            else:
                style = "border-radius: 0px;"
            WidgetFactory.create_icon(
                btn_ref,
                image_loc1,
                50,
                20,
                True,
                image_loc2,
                False,
            )
            additional_style = (
                "QPushButton { "
                + f"{style} padding: 5px 5px ; background: #DEDEDE; border-bottom: 1px solid #f58220; "
                + "} "
            )
            StyleHelper.set_tool_tip(btn_ref, tool_tip, additional_style)
            self.form_actions_btn_inner_layout.addWidget(btn_ref)

    def init_thread_controls(self) -> None:
        """
        Initializes controls such as the start/stop buttons and the progress bar.
        """
        self.start = GradientButton(
            "",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.stop = GradientButton(
            "",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.monitor = GradientButton(
            "",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        StyleHelper.set_tool_tip(self.stop, "Stop Runner", "")
        StyleHelper.set_tool_tip(self.start, "Start Runner", "")
        StyleHelper.set_tool_tip(self.monitor, "Monitor Runner", "")
        WidgetFactory.create_icon(
            self.start,
            ":/images/play.png",
            20,
            20,
            True,
            False,
        )
        WidgetFactory.create_icon(
            self.monitor,
            ":/images/monitor.png",
            20,
            20,
            True,
            False,
        )
        WidgetFactory.create_icon(
            self.stop,
            ":/images/stop.png",
            20,
            20,
            True,
            False,
        )

        self.monitor.setFixedWidth(50)
        self.monitor.setFixedHeight(30)
        self.monitor.setProperty("page_action", RULESPAGEEVENT.TOGGLE_DISPLAY_MONITOR)
        self.stop.setFixedWidth(30)
        self.stop.setFixedHeight(30)
        self.stop.setProperty("page_action", RULESPAGEEVENT.STOP_RUNNER)
        self.start.setFixedHeight(30)
        self.stop.setHidden(True)
        self.start.setChecked(True)
        self.start.setProperty("page_action", RULESPAGEEVENT.START_RUNNER)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setHidden(True)
        bottom_h_layout = QHBoxLayout()
        bottom_h_layout.setSpacing(5)

        bottom_h_layout.addWidget(self.progress_bar)

        thread_controls = QHBoxLayout()
        thread_controls.addWidget(self.monitor)
        thread_controls.addWidget(self.start)
        thread_controls.addWidget(self.stop)
        thread_controls.setSpacing(1)
        thread_controls.setContentsMargins(0, 0, 0, 0)
        self.start.setFixedWidth(75)

        bottom_h_layout.addLayout(thread_controls)
        bottom_h_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(bottom_h_layout)

    @Slot(object)
    def handle_rule_runner_state_update(self, state: RULERUNNERLIFECYCLE) -> None:
        if state == RULERUNNERLIFECYCLE.STARTED:
            self.stop.setHidden(False)
            self.progress_bar.setHidden(False)
            self.start.setDisabled(True)
        if state == RULERUNNERLIFECYCLE.FINISHED:
            self.stop.setHidden(True)
            self.start.setDisabled(False)
            QTimer.singleShot(5000, lambda: self.progress_bar.setHidden(True))

    @Slot(int, int)
    def set_progress_bar(self, current: int, total: int) -> None:
        """
        Updates the rules progress bar.
        """
        self.progress_bar.setHidden(False)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)

    @Slot(object)
    def update_form_validation(self, errors_result: ValidationRulesResult):
        all_errors = []
        for guid, errors in errors_result.errors_by_rule.items():
            form = self.stacked_widget.get_form_by_guid(guid)
            if form:
                all_errors.extend(errors)
                form.highlight_errors(errors)

        self._form_errors = all_errors
        if all_errors:
            self.validate_feedback.setText(f" Total Errors : {len(all_errors)}")
            self.validate_feedback.setIcon(self.error_icon)
        else:
            self.validate_feedback.setText(" No Errors Found")
            self.validate_feedback.setIcon(self.no_error_icon)
        self.set_hidden_errors_dialog_btn(True if not all_errors else False)

    def handle_action_button_click(self):
        sender = self.sender()
        if sender is None:
            return

        raw_action = sender.property("page_action")
        if raw_action is None:
            return

        action = RULESPAGEEVENT(raw_action)
        payload = self._build_action_payload(action)
        if payload is None:
            return
        self.rules_page_action.emit(payload)

    def _build_action_payload(self, action: RULESPAGEEVENT):

        validate_actions = (
            RULESPAGEEVENT.START_RUNNER,
            RULESPAGEEVENT.SYS_SAVE_RULES,
            RULESPAGEEVENT.USER_SAVE_RULES,
            RULESPAGEEVENT.VALIDATE_RULES,
        )

        if action in validate_actions:
            return RulesPageAction[object](action, self.extract_forms_to_dict())

        if action == RULESPAGEEVENT.DELETE_ALL_RULES:
            self.delete_all_forms()
            return RulesPageAction[None](action, None)

        if action == RULESPAGEEVENT.DELETE_RULE:
            guid = self.on_delete_rule()
            return RulesPageAction[str](action, guid)

        if action == RULESPAGEEVENT.CLONE_RULE:
            form = self.stacked_widget.get_form_by_index(
                self.stacked_widget.currentIndex()
            )
            return RulesPageAction[str](action, form.guid)

        if action == RULESPAGEEVENT.BOOKMARK_RULES:
            self.rule_set_dialog.show()
            return

        if action == RULESPAGEEVENT.STOP_RUNNER:
            return RulesPageAction[None](action, None)

        if action == RULESPAGEEVENT.TOGGLE_DISPLAY_MONITOR:
            return RulesPageAction[None](action, None)

    def handle_bookmark_rules(self, rule_set_name, rule_set_desc):
        payload = RulesPageAction[str](
            RULESPAGEEVENT.BOOKMARK_RULES,
            {
                "rule_set_name": rule_set_name,
                "rule_set_description": rule_set_desc,
                "rules": self.extract_forms_to_dict(),
            },
        )
        self.rules_page_action.emit(payload)

    @Slot(str, str)
    def focus_changed(self, rule_guid: str, full_path: str) -> None:
        """
        Slot to handle when focus changes between form fields. Updates the current focused
        object's name and text.
        """
        self._event_guid = rule_guid
        self._event_path = full_path

    def handle_copy_fields(self) -> None:
        """
        Copy the value from the currently focused field across all rules in the form.
        """
        if self._event_guid is None or self._event_path is None:
            return

        to_copy_adapter = self.stacked_widget.get_form_by_guid(self._event_guid)
        value = to_copy_adapter.field_registry.get_text_value(self._event_path)

        rule_adapters = self.stacked_widget.get_form_factories()
        for adapter in rule_adapters:
            if adapter.guid == self._event_guid:
                continue
            adapter.field_registry.set_text_value(self._event_path, value)

    def extract_forms_to_dict(self):
        rule_forms = self.get_forms()
        return {"rules": [form.to_validation_dict() for form in rule_forms]}

    def delete_all_forms(self) -> None:
        """Deletes all rule forms from the UI."""
        self.stacked_widget.remove_all()
        # self.current_rule_index = 0
        self.set_up_rules([])
        self.update_navigation_buttons()

    @Slot(list)
    def rules_changed(self, rules: List[dict]) -> None:
        """
        Updates the UI when the rules are changed.
        """
        self.stacked_widget.remove_all()
        if not len(rules) - 1 > self.current_rule_index:
            self.current_rule_index = 0
        self.set_up_rules(rules)
        self.rules_form_updated.emit()

    def set_hidden_errors_dialog_btn(self, state: bool) -> None:
        """
        Sets the visibility of the error dialog button.
        """
        self.validate_open_dialog.setHidden(state)

    def get_forms(self) -> List[RuleAdapter]:
        """
        Retrieves the list of form objects currently displayed in the UI.
        """
        return self.stacked_widget.get_form_factories()

    def repaint_shadow(self) -> None:
        """Repaint shadow of widget. Used for repainting shadow after the scroll bar moves"""
        self.editor_widget.update()

    def on_delete_rule(self) -> str:
        """Handles the deletion of a rule from the UI."""
        if self.stacked_widget.get_form_factories():
            current_index = self.stacked_widget.currentIndex()
            rule_form = self.stacked_widget.get_form_by_index(current_index)
            if current_index > 0:
                previous_form = self.stacked_widget.get_form_by_index(current_index - 1)
                self.previous_guid = previous_form.guid
            guid = rule_form.guid
            self.delete_all_forms()
        return guid

    def set_disable_action_btns(self) -> None:
        """Enables or disables the action buttons based on the presence of rules.

        Returns:
            None: This function does not return a value.
        """
        actions_buttons = [
            self.download,
            self.validate,
            self.clone,
            self.copy_field,
            self.trash,
            self.delete_all,
            self.bookmark,
        ]
        for btn in actions_buttons:
            if self.stacked_widget.get_form_factories():
                btn.setDisabled(False)

            else:
                btn.setDisabled(True)

    def set_up_rules(self, rules: list[Rule]) -> None:
        """
        Sets up the UI with the provided rules.
        """
        if rules:
            self.stacked_widget.remove_by_name("No-Rules-Widget")
            for rule in rules:
                registry = RuleFieldRegistry()
                widget = RuleFactory(registry, self.event_filter).build(
                    rule, "margin-top: 0px; padding-left: 0px;padding-top: 0px;"
                )
                adapter = RuleAdapter(
                    guid=rule.guid,
                    widget=widget,
                    field_registry=registry,
                )
                self.stacked_widget.add_form(adapter)
            if self.previous_guid:
                index = self.stacked_widget.get_widget_index_by_guid(self.previous_guid)
                if index > -1:
                    self.stacked_widget.setCurrentIndex(index)
            self.update_navigation_buttons()
        else:

            self.setup_no_rules_widget()
        self.set_disable_action_btns()

    def setup_no_rules_widget(self) -> None:
        """Displays a widget when no rules are available."""
        self.no_rules_widget = QWidget()
        self.no_rules_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        nr_widget_layout = QHBoxLayout(self.no_rules_widget)
        self.no_rules_label = QLabel(
            "Open a File or Add a Rule to Get Started with Creating Rules."
        )
        nr_widget_layout.addWidget(self.no_rules_label, Qt.AlignmentFlag.AlignTop)
        self.no_rules_label.setStyleSheet(
            "background: transparent; padding-left: 1.5em; color: white"
        )
        self.no_rules_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.stacked_widget.add_widget("No-Rules-Widget", self.no_rules_widget)
        self.repaint_shadow()

    def update_navigation_buttons(self) -> None:
        """Updates the state of the navigation buttons (previous/next)."""

        self.current_rule_index = self.stacked_widget.currentIndex()
        self.prev_button.setDisabled(self.current_rule_index == 0)
        self.next_button.setDisabled(
            self.current_rule_index >= self.stacked_widget.count() - 1
        )
        if self.stacked_widget.count() > 0:
            self.nav_label.setText(
                f"Rule: {self.stacked_widget.currentIndex() +1} / {self.stacked_widget.count()}"
            )
        else:
            self.nav_label.setText("")

    def show_previous_rule(self) -> None:
        """Navigates to the previous rule in the UI."""
        if self.current_rule_index > 0:
            self.current_rule_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.previous_guid = self.stacked_widget.get_form_by_index(
                self.current_rule_index
            ).guid

        self.update_navigation_buttons()

    def show_next_rule(self) -> None:
        """Navigates to the next rule in the UI."""
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.previous_guid = self.stacked_widget.get_form_by_index(
                self.current_rule_index
            ).guid

            self.prev_button.setDisabled(False)
        self.update_navigation_buttons()

    def display_errors_dialog(self) -> None:
        """
        Display the error dialog if validation errors are found in the form fields.
        """
        add = SchemaErrorDialog(self._form_errors, self)
        self.set_hidden_errors_dialog_btn(False)
        add.show()
