from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy, QTextEdit, QVBoxLayout

from ...helpers import WidgetFactory
from ..gradient_dialog import GradientDialog
from .message_dialog_css import STYLES


class MessageDialog(GradientDialog):

    def __init__(self, title, message, parent=None):
        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)
        self.title = title
        self.setFixedHeight(200)
        self.setFixedWidth(400)
        self.setWindowTitle(self.title)
        self.message = message

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
        inner_layout.setSpacing(0)

        message_text_edit = QTextEdit(self.message)
        message_text_edit.setObjectName("error-text-edit")
        message_text_edit.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )
        message_text_edit.setReadOnly(True)

        inner_layout.addRow(message_text_edit)

        self.close_btn = QPushButton("Close")
        self.close_btn.setObjectName("close-btn")
        outter_layout.addRow(self.close_btn)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
