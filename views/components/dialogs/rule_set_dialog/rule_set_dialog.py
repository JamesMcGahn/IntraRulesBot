from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...helpers import WidgetFactory
from ..gradient_dialog import GradientDialog
from .rule_set_css import STYLES


class RuleSetDialog(GradientDialog):
    """
    A custom dialog for displaying a message with a gradient background.
    """

    send_form = Signal(str, str)

    def __init__(self, parent: Optional[QWidget] = None):
        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)
        self.title = "Save to Rule Sets"
        self.setFixedWidth(400)
        self.setWindowTitle(self.title)
        self.message = "Msg"

        self.setStyleSheet(STYLES)

        self.settings_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WA_StyledBackground, True)
        outter_layout = WidgetFactory.create_form_box(
            self.title,
            self.settings_layout,
            False,
            object_name="Error-Outer",
            title_color="#fcfcfc",
            title_font_size=18,
        )

        outter_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            max_width=350,
        )
        inner_layout.setContentsMargins(5, 5, 5, 5)
        inner_layout.setSpacing(5)
        inner_widget = QWidget()
        inner_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        inner_widget_layout = QFormLayout(inner_widget)
        inner_widget_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.rule_set_input = QLineEdit()
        rule_set_label = QLabel("Rule Set Name:")
        self.rule_set_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.rule_set_desc_input = QTextEdit()
        self.rule_set_desc_input.setFixedHeight(75)
        rule_set_desc_label = QLabel("Description:")

        inner_widget_layout.addRow(rule_set_label, self.rule_set_input)
        inner_widget_layout.addRow(rule_set_desc_label, self.rule_set_desc_input)

        inner_layout.addRow(inner_widget)

        self.close_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel-btn")
        self.close_btn.setObjectName("close-btn")
        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.close_btn)

        outter_layout.addRow(btn_box)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.send_form_data)

        self.cancel_btn.clicked.connect(self.handle_cancel_clicked)

    def handle_cancel_clicked(self):
        self.clear_form()
        self.reject()

    def clear_form(self):
        self.rule_set_input.setText("")
        self.rule_set_desc_input.setText("")

    def send_form_data(self):
        validated = True
        if not self.rule_set_input.text().strip():
            self.rule_set_input.setStyleSheet("border: 1px solid red")
            validated = False
        else:
            self.rule_set_input.setStyleSheet("border: 1px solid green")

        if not self.rule_set_desc_input.toPlainText().strip():
            self.rule_set_desc_input.setStyleSheet("border: 1px solid red")
            validated = False
        else:
            self.rule_set_desc_input.setStyleSheet("border: 1px solid green")

        if validated:
            self.send_form.emit(
                self.rule_set_input.text(), self.rule_set_desc_input.toPlainText()
            )
            self.clear_form()
            self.accept()
