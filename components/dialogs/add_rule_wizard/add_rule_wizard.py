import os
import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...helpers import StyleHelper, WidgetFactory
from ...toasts import QToast
from ..gradient_dialog import GradientDialog


class AddRuleWizard(GradientDialog):
    submit_form = Signal(object)

    def __init__(self, parent=None):
        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "add_rule_wizard.css")
        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.setWindowTitle("Add New Rule Wizard")
        self.setMinimumHeight(400)
        self.setFixedWidth(400)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout = QHBoxLayout(self)
        self.setContentsMargins(0, 5, 0, 5)
        general_settings = WidgetFactory.create_form_box(
            "",
            self.main_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            max_width=400,
            object_name="Main-Add-Group-Box",
            style_sheet="QGroupBox#Main-Add-Group-Box {padding: 5px;margin-top: 5px;} ",
        )
        general_settings.setSpacing(5)
        rule_name_lbl = QLabel("Rule Name:")
        self.rule_name_input = QLineEdit()
        general_settings.addRow(rule_name_lbl, self.rule_name_input)
        self.trigger = QComboBox()
        trigger_lbl = QLabel("Trigger:")
        self.trigger.addItem("Frequency")
        # self.trigger.addItem("Action")
        general_settings.addRow(trigger_lbl, self.trigger)

        add_conditions_lbl = QLabel("Add Condition:")
        add_conditions_btn = QPushButton("Add")
        StyleHelper.drop_shadow(add_conditions_btn)
        reset_conditions = QPushButton("Reset")
        StyleHelper.drop_shadow(reset_conditions)
        conditions_h_layout = QHBoxLayout()
        conditions_h_layout.addWidget(add_conditions_btn)
        conditions_h_layout.addWidget(reset_conditions)

        general_settings.addRow(add_conditions_lbl, conditions_h_layout)
        add_conditions_btn.clicked.connect(self.add_condition)

        self.conditions_box = QWidget()
        self.conditions_box.setContentsMargins(1, 1, 1, 1)

        self.conditions_box.setMinimumHeight(150)
        self.conditions_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        conditions_v = QVBoxLayout(self.conditions_box)
        conditions_v.setContentsMargins(0, 0, 0, 0)
        self.conditions_layout = QFormLayout()
        self.conditions_layout.setContentsMargins(0, 0, 0, 0)
        conditions_v.addLayout(self.conditions_layout)
        conditions_v.setAlignment(Qt.AlignTop)

        reset_conditions.clicked.connect(
            lambda event: self.on_reset_btn_clicked(event, self.conditions_layout)
        )

        general_settings.addRow(self.conditions_box)

        add_actions_lbl = QLabel("Add actions:")
        add_actions_btn = QPushButton("Add")
        StyleHelper.drop_shadow(add_actions_btn)
        reset_actions = QPushButton("Reset")
        StyleHelper.drop_shadow(reset_actions)
        actions_h_layout = QHBoxLayout()
        actions_h_layout.addWidget(add_actions_btn)
        actions_h_layout.addWidget(reset_actions)

        general_settings.addRow(add_actions_lbl, actions_h_layout)
        add_actions_btn.clicked.connect(self.add_action)

        self.actions_box = QWidget()
        self.actions_box.setMinimumHeight(150)
        self.actions_box.setContentsMargins(1, 1, 1, 1)
        self.actions_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.actions_layout = QFormLayout(self.actions_box)

        reset_actions.clicked.connect(
            lambda event: self.on_reset_btn_clicked(event, self.actions_layout)
        )

        general_settings.addRow(self.actions_box)
        submit_button = QPushButton("Submit")
        StyleHelper.drop_shadow(submit_button)

        general_settings.addRow(submit_button)
        submit_button.clicked.connect(self.on_submit)

    def add_condition(self):
        condition_type_lbl = QLabel("Condition Type:")
        condition_type = QComboBox()
        condition_type.addItem("stats")

        self.conditions_layout.addRow(condition_type_lbl, condition_type)

    def add_action(self):
        action_type_lbl = QLabel("Action Type:")
        action_type = QComboBox()
        action_type.addItem("email")

        self.actions_layout.addRow(action_type_lbl, action_type)

    def remove_layout_items(self, layout):
        # Iterate over all items in the form layout and remove them

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.remove_layout_items(item.layout())

    def on_reset_btn_clicked(self, event, layout):
        self.remove_layout_items(layout)

    def get_all_rows(self, layout, parent_type):
        # Iterate over all rows in the QFormLayout

        fields = []

        row_count = layout.rowCount()
        for index in range(row_count):
            # Get the label and field for each row
            # label_item = layout.itemAt(index, QFormLayout.LabelRole)
            field_item = layout.itemAt(index, QFormLayout.FieldRole)

            # label_widget = label_item.widget() if label_item is not None else None
            field_widget = field_item.widget() if field_item is not None else None

            if isinstance(field_widget, QComboBox):
                fields.append({"details": {parent_type: field_widget.currentText()}})
        return fields

    def on_submit(self):
        actions = self.get_all_rows(self.actions_layout, "action_type")

        if not actions:
            QToast(
                self, "error", "Form not submitted", "At least one Action is needed."
            )
            return
        form = {
            "rule_name": self.rule_name_input.text(),
            "guid": str(uuid.uuid4()),
            "frequency_based": True,
            "conditions": self.get_all_rows(self.conditions_layout, "condition_type"),
            "actions": actions,
        }

        self.submit_form.emit(form)

        self.remove_layout_items(self.conditions_layout)
        self.remove_layout_items(self.actions_layout)
        self.rule_name_input.setText("")
        self.accept()
