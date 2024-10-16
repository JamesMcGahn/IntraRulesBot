from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...helpers import WidgetFactory
from ..gradient_dialog import GradientDialog
from .confirmation_dialog_css import STYLES


class ConfirmationDialog(GradientDialog):
    """
    A custom dialog for displaying a confirmation message with a gradient background.

    Args:
        title (str): The title of the dialog window.
        message (str): The message to display in the dialog.
        accept_btn_text (str, optional): button text for the accept button. Default's to Accept.
        parent (Optional[QWidget]): The parent widget of the dialog, defaults to None.
    """

    def __init__(
        self,
        title: str,
        message: str,
        accept_btn_text: str = "Accept",
        parent: Optional[QWidget] = None,
    ):
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

        self.close_btn = QPushButton(accept_btn_text)
        self.close_btn.setObjectName("close-btn")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel-btn")
        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.close_btn)

        outter_layout.addRow(btn_box)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
