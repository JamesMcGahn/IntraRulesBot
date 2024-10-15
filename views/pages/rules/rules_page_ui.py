import uuid
from typing import List

from PySide6.QtCore import QSize, Qt, Signal, Slot
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

from components.buttons import EditorActionButton, GradientButton
from components.dialogs import AddRuleWizard
from components.helpers import StyleHelper, WidgetFactory
from components.layouts import ScrollArea, StackedFormWidget
from managers import RuleFormManager
from translators import GenerateRuleObject


class RulesPageView(QWidget):
    """
    A view class that provides the UI for managing rules in the application.
    This view includes buttons for navigating, adding, cloning, deleting, and saving rules,
    along with a validation feedback button and a progress bar for operations.

    Signals:
        delete_rule: Signal emitted when the delete rule action is triggered.
        rules_form_updated: Signal emitted when a rule is added
    """

    delete_rule = Signal()
    rules_form_updated = Signal()

    def __init__(self):
        """
        Initializes the UI components for the RulesPageView.
        """
        super().__init__()
        self.current_rule_index = 0

        self.init_ui()

    def init_ui(self) -> None:
        """
        Sets up the UI layout and widgets for the rules page, including editor buttons,
        navigation buttons, and rule actions.
        """
        self.current_rule_index = 0

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

        self.add_rule = AddRuleWizard()
        self.add_rule.submit_form.connect(self.add_rule_form_submit)

        # Signal / Slot Connections
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.repaint_shadow)
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.repaint_shadow)
        self.trash.clicked.connect(self.on_delete_rule)
        self.prev_button.clicked.connect(self.show_previous_rule)
        self.next_button.clicked.connect(self.show_next_rule)
        self.delete_all.clicked.connect(self.delete_all_forms)
        self.add.clicked.connect(self.show_add_rule_dialog)
        self.clone.clicked.connect(self.clone_rule)
        # Setup
        self.update_navigation_buttons()

    def setup_actions_buttons(self) -> None:
        """
        Sets up action buttons for rule management (e.g., add, save, delete).

        Returns:
            None: This function does not return a value.
        """

        self.form_actions_btn_inner_layout.setSpacing(0)
        self.form_actions_btn_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.add = EditorActionButton("")
        self.save = EditorActionButton("")
        self.download = EditorActionButton("")
        self.validate = EditorActionButton("")
        self.clone = EditorActionButton("")
        self.copy_field = EditorActionButton("")
        self.trash = EditorActionButton("")
        self.delete_all = EditorActionButton("")

        actionBtns = [
            (
                self.add,
                "Add Rule",
                ":/images/add_off_b.png",
                ":/images/add_on.png",
            ),
            (
                self.save,
                "Save",
                ":/images/save_off_b.png",
                ":/images/save_on.png",
            ),
            (
                self.validate,
                "Validate Fields",
                ":/images/validate_off_b.png",
                ":/images/validate_on.png",
            ),
            (
                self.clone,
                "Clone Rule",
                ":/images/clone_off_b.png",
                ":/images/clone_on.png",
            ),
            (
                self.copy_field,
                "Apply Field Value Across Rules",
                ":/images/copy_field_off_b.png",
                ":/images/copy_field_on.png",
            ),
            (
                self.trash,
                "Delete Rule",
                ":/images/trash_off_b.png",
                ":/images/trash_on.png",
            ),
            (
                self.download,
                "Save to File",
                ":/images/download_off_b.png",
                ":/images/download_on.png",
            ),
            (
                self.delete_all,
                "Delete All Rules",
                ":/images/delete_all_off_b.png",
                ":/images/delete_all_on.png",
            ),
        ]

        for index, btn in enumerate(actionBtns):
            btn_ref, tool_tip, image_loc1, image_loc2 = btn

            btn_ref.setToolTip(tool_tip)
            btn_ref.setFixedWidth(40)
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
            btn_ref.setStyleSheet(
                "QPushButton { "
                + f"{style} padding: 5px 5px ; background: #DEDEDE; border-bottom: 1px solid #f58220; "
                + "} QToolTip"
                + "{ background: #DEDEDE; color: black; border: 1px solid #f58220; border-radius: 0px; padding: 5px; }"
            )
            self.form_actions_btn_inner_layout.addWidget(btn_ref)

    def init_thread_controls(self) -> None:
        """
        Initializes controls such as the start/stop buttons and the progress bar.

        Returns:
            None: This function does not return a value.
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
        WidgetFactory.create_icon(
            self.start,
            ":/images/play.png",
            50,
            20,
            True,
            False,
        )
        WidgetFactory.create_icon(
            self.stop,
            ":/images/stop.png",
            50,
            20,
            True,
            False,
        )
        self.stop.setFixedWidth(30)
        self.start.setChecked(True)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setHidden(True)
        bottom_h_layout = QHBoxLayout()
        bottom_h_layout.setSpacing(5)
        thread_controls = QHBoxLayout()
        bottom_h_layout.addWidget(self.progress_bar)

        thread_controls.addWidget(self.start)
        thread_controls.addWidget(self.stop)
        thread_controls.setSpacing(1)
        thread_controls.setContentsMargins(0, 0, 0, 0)
        self.start.setFixedWidth(75)

        bottom_h_layout.addLayout(thread_controls)
        bottom_h_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(bottom_h_layout)

    @Slot(int, int)
    def set_progress_bar(self, current: int, total: int) -> None:
        """
        Updates the rules progress bar.
        Args:
            current (int): The current progress.
            total (int): The total value for the progress bar.

        Returns:
            None: This function does not return a value.
        """
        if current < total:
            self.progress_bar.setHidden(False)
        else:
            self.progress_bar.setHidden(True)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)

    def clone_rule(self) -> None:
        """Clones the currently selected rule and adds it to the rule list.

        Returns:
            None: This function does not return a value.
        """
        form = self.stacked_widget.get_form_by_index(self.stacked_widget.currentIndex())
        data = form.create_input_dict()
        data["guid"] = str(uuid.uuid4())
        self.current_rule_index = self.stacked_widget.count()
        self.rules_changed([data])
        self.stacked_widget.setCurrentIndex(self.current_rule_index)
        self.update_navigation_buttons()

    def show_add_rule_dialog(self) -> None:
        """Displays the dialog to add a new rule.

        Returns:
            None: This function does not return a value.
        """
        self.add_rule.show()

    @Slot(object)
    def add_rule_form_submit(self, form: object) -> None:
        """
        Handles the submission of a new rule form.

        Args:
            form (object): The form object containing rule data.

        Returns:
            None: This function does not return a value.
        """
        add = GenerateRuleObject(form)
        current_count = self.stacked_widget.count()
        new_rule = add.generate_dynamic_object()

        if new_rule:
            self.rules_changed([new_rule])
            self.current_rule_index = current_count
            self.stacked_widget.setCurrentIndex(current_count)
            self.update_navigation_buttons()

    def delete_all_forms(self) -> None:
        """Deletes all rule forms from the UI.

        Returns:
            None: This function does not return a value.
        """
        self.stacked_widget.remove_all()
        self.current_rule_index = 0
        self.set_up_rules([])
        self.update_navigation_buttons()

    @Slot(list)
    def rules_changed(self, rules: List[dict]) -> None:
        """
        Updates the UI when the rules are changed.

        Args:
            rules (List[dict]): A list of rule dictionaries.

        Returns:
            None: This function does not return a value.
        """
        self.set_up_rules(rules)
        self.rules_form_updated.emit()

    def set_hidden_errors_dialog_btn(self, state: bool) -> None:
        """
        Sets the visibility of the error dialog button.

        Args:
            state (bool): If True, hides the button; otherwise, shows the button.

        Returns:
            None: This function does not return a value.
        """
        self.validate_open_dialog.setHidden(state)

    def get_forms(self) -> List[object]:
        """
        Retrieves the list of form objects currently displayed in the UI.

        Returns:
            List[object]: The list of form objects.
        """
        return self.stacked_widget.get_form_factories()

    def repaint_shadow(self) -> None:
        """Repaint shadow of widget. Used for repainting shadow after the scroll bar moves

        Returns:
            None: This function does not return a value.
        """
        self.editor_widget.update()

    def on_delete_rule(self) -> None:
        """Handles the deletion of a rule from the UI.

        Returns:
            None: This function does not return a value.
        """
        if self.stacked_widget.get_form_factories():
            self.stacked_widget.remove_form_by_index(self.stacked_widget.currentIndex())
            self.update_navigation_buttons()
            if self.stacked_widget.count() == 0:
                self.setup_no_rules_widget()

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
        ]
        for btn in actions_buttons:
            if self.stacked_widget.get_form_factories():
                btn.setDisabled(False)

            else:
                btn.setDisabled(True)

    def set_up_rules(self, rules: List[dict]) -> None:
        """
        Sets up the UI with the provided rules.

        Args:
            rules (List[dict]): A list of rule dictionaries.

        Returns:
            None: This function does not return a value.
        """
        if rules:
            self.stacked_widget.remove_by_name("No-Rules-Widget")
            for rule in rules:
                rule_form = RuleFormManager(rule)
                self.stacked_widget.add_form(
                    rule_form, "margin-top: 0px; padding-left: 0px;padding-top: 0px;"
                )

            self.update_navigation_buttons()
        else:
            self.setup_no_rules_widget()
        self.set_disable_action_btns()

    def setup_no_rules_widget(self) -> None:
        """Displays a widget when no rules are available.

        Returns:
            None: This function does not return a value.
        """
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
        """Updates the state of the navigation buttons (previous/next).

        Returns:
            None: This function does not return a value.
        """
        self.prev_button.setDisabled(self.current_rule_index == 0)

        self.next_button.setDisabled(
            self.current_rule_index >= self.stacked_widget.count() - 1
        )
        if self.stacked_widget.count() > 0:
            self.nav_label.setText(
                f"Rule: {self.current_rule_index+1} / {self.stacked_widget.count()}"
            )
        else:
            self.nav_label.setText("")

    def show_previous_rule(self) -> None:
        """Navigates to the previous rule in the UI.

        Returns:
            None: This function does not return a value.
        """
        if self.current_rule_index > 0:
            self.current_rule_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)

        self.update_navigation_buttons()

    def show_next_rule(self) -> None:
        """Navigates to the next rule in the UI.

        Returns:
            None: This function does not return a value.
        """
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)

            self.prev_button.setDisabled(False)
        self.update_navigation_buttons()
