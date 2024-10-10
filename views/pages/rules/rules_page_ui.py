from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
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
    delete_rule = Signal()

    def __init__(self):
        super().__init__()
        self.current_rule_index = 0

        self.init_ui()

    def init_ui(self):
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

        form_actions_btn_inner_layout = QVBoxLayout(actions_btn_widget_inner)
        form_actions_btn_inner_layout.setSpacing(0)
        form_actions_btn_inner_layout.setContentsMargins(0, 0, 0, 0)
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
                + "{ background: transparent; color: black; border: 1px solid #f58220; border-radius: 0px; padding: 5px; }"
            )
            form_actions_btn_inner_layout.addWidget(btn_ref)

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
        # Setup
        self.update_navigation_buttons()

    def show_add_rule_dialog(self):
        self.add_rule.show()

    @Slot(object)
    def add_rule_form_submit(self, form):
        add = GenerateRuleObject(form)
        current_count = self.stacked_widget.count()
        new_rule = add.generate_dynamic_object()

        if new_rule:
            self.rules_changed([new_rule])
            self.current_rule_index = current_count
            self.stacked_widget.setCurrentIndex(current_count)
            self.update_navigation_buttons()

    def delete_all_forms(self):
        self.stacked_widget.remove_all()
        self.current_rule_index = 0
        self.set_up_rules([])
        self.update_navigation_buttons()

    @Slot(list)
    def rules_changed(self, rules):
        self.set_up_rules(rules)

    def set_hidden_errors_dialog_btn(self, state):
        self.validate_open_dialog.setHidden(state)

    def get_forms(self):
        return self.stacked_widget.get_form_factories()

    def repaint_shadow(self):
        """Repaint shadow of widget. Used for repainting shadow after the scroll bar moves"""
        self.editor_widget.update()

    def on_delete_rule(self):
        if self.stacked_widget.get_form_factories():
            self.stacked_widget.remove_form_by_index(self.stacked_widget.currentIndex())
            self.update_navigation_buttons()
            if self.stacked_widget.count() == 0:
                self.setup_no_rules_widget()

    def set_disable_action_btns(self):
        actions_buttons = [
            self.save,
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

    def set_up_rules(self, rules):
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

    def setup_no_rules_widget(self):
        self.no_rules_widget = QWidget()
        nr_widget_layout = QHBoxLayout(self.no_rules_widget)
        self.no_rules_label = QLabel(
            "Open a File or Add a Rule to Get Started with Creating Rules."
        )
        nr_widget_layout.addWidget(self.no_rules_label, Qt.AlignmentFlag.AlignTop)
        self.no_rules_label.setStyleSheet("background: #DEDEDE; padding-left: 1.5em;")
        self.no_rules_label.setMaximumHeight(60)
        self.no_rules_label.setMaximumWidth(400)
        self.stacked_widget.add_widget("No-Rules-Widget", self.no_rules_widget)
        self.repaint_shadow()

    def update_navigation_buttons(self):
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

    def show_previous_rule(self):
        if self.current_rule_index > 0:
            self.current_rule_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)

        self.update_navigation_buttons()

    def show_next_rule(self):
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)

            self.prev_button.setDisabled(False)
        self.update_navigation_buttons()
