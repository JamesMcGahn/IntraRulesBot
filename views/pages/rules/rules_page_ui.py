from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.helpers import WidgetFactory
from components.layouts import ScrollArea, StackedFormWidget
from managers import RuleFormManager


class RulesPageView(QWidget):
    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.current_rule_index = 0
        self.rules_inputs = []
        self.rules = []
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

        self.stacked_widget = StackedFormWidget()
        self.stacked_widget.setObjectName("Rules-Stacked-Widget")
        self.stacked_widget.setContentsMargins(10, 10, 15, 10)
        self.no_rules_label = QLabel("Open a File or Add a Rule.")

        scroll_area = ScrollArea(self)
        scroll_area.setWidget(self.stacked_widget)

        # TODO: call UI dropshadow helper
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(5)
        shadow_effect.setXOffset(3)
        shadow_effect.setYOffset(3)
        shadow_effect.setColor(QColor(0, 0, 0, 60))
        scroll_area.setGraphicsEffect(shadow_effect)

        self.set_up_rules()

        top_button_bar_layout = QHBoxLayout()
        h_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)

        form_actions_btn_layout = QHBoxLayout()
        form_actions_btn_layout.setSpacing(2)
        self.download = QPushButton()
        self.download.setToolTip("Save to File")
        self.download.setFixedWidth(30)
        WidgetFactory.create_icon(self.download, ":/images/download.png", 50, 20)
        self.clone = QPushButton()
        self.clone.setFixedWidth(30)
        self.clone.setToolTip("Clone Rule")
        WidgetFactory.create_icon(self.clone, ":/images/clone.png", 50, 20)
        self.copy_field = QPushButton()
        self.copy_field.setFixedWidth(30)
        self.copy_field.setToolTip("Apply Field Value Across Rules")
        WidgetFactory.create_icon(self.copy_field, ":/images/copy_field.png", 50, 20)
        self.save = QPushButton()
        self.save.setFixedWidth(30)
        self.save.setToolTip("Save")
        WidgetFactory.create_icon(self.save, ":/images/save.png", 50, 20)
        self.trash = QPushButton()
        self.trash.setFixedWidth(30)
        self.trash.setToolTip("Delete Rule")
        WidgetFactory.create_icon(self.trash, ":/images/trash.png", 50, 20)
        self.validate = QPushButton()
        self.validate.setFixedWidth(30)
        self.validate.setToolTip("Validate Rule")
        WidgetFactory.create_icon(self.validate, ":/images/validate.png", 50, 20)
        form_actions_btn_layout.addWidget(self.save)
        form_actions_btn_layout.addWidget(self.download)
        form_actions_btn_layout.addWidget(self.validate)
        form_actions_btn_layout.addWidget(self.clone)
        form_actions_btn_layout.addWidget(self.copy_field)
        form_actions_btn_layout.addWidget(self.trash)

        top_button_bar_layout.addLayout(form_actions_btn_layout)
        top_button_bar_layout.addItem(h_spacer)

        self.validate_feedback = QPushButton()
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

        top_button_bar_layout.addWidget(self.validate_feedback)
        top_button_bar_layout.addItem(h_spacer)

        nav_btn_layout = QHBoxLayout()
        self.nav_label = QLabel()
        self.nav_label.setStyleSheet("background: transparent;")
        self.prev_button = QPushButton()
        self.next_button = QPushButton()
        self.prev_button.clicked.connect(self.show_previous_rule)
        self.next_button.clicked.connect(self.show_next_rule)
        nav_btn_layout.addWidget(self.nav_label)
        nav_btn_layout.addWidget(self.prev_button)
        nav_btn_layout.addWidget(self.next_button)
        self.prev_button.setFixedWidth(50)
        self.next_button.setFixedWidth(50)
        WidgetFactory.create_icon(self.prev_button, ":/images/left_arrow.png", 50, 20)
        WidgetFactory.create_icon(self.next_button, ":/images/right_arrow.png", 50, 20)

        top_button_bar_layout.addLayout(nav_btn_layout)

        bottom_btn_layout = QHBoxLayout()

        self.main_layout.addLayout(top_button_bar_layout)
        self.main_layout.addWidget(scroll_area)
        self.main_layout.addLayout(bottom_btn_layout)
        self.update_navigation_buttons()

        self.outter_layout.addRow(self.main_layout)

    def set_up_rules(self):
        if self.rules:
            self.stacked_widget.remove_by_name("No-Rules-Widget")

            for rule in self.rules:
                rule_form = RuleFormManager(rule)
                self.stacked_widget.add_form(rule_form)

            self.update_navigation_buttons()
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
            )
        else:
            self.stacked_widget.add_widget("No-Rules-Widget", self.no_rules_label)

    @Slot(list)
    def rules_changed(self, rules):
        print(rules)
        self.rules = rules
        self.set_up_rules()

    def update_navigation_buttons(self):
        self.prev_button.setDisabled(self.current_rule_index == 0)
        self.next_button.setDisabled(
            self.current_rule_index >= self.stacked_widget.count() - 1
        )

    def show_previous_rule(self):
        if self.current_rule_index > 0:
            self.current_rule_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
            )
        self.update_navigation_buttons()

    def show_next_rule(self):
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
            )
            self.prev_button.setDisabled(False)
        self.update_navigation_buttons()
