from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from services.validator import SchemaValidator

from ...helpers import WidgetFactory
from ...layouts import ScrollArea
from ..gradient_dialog import GradientDialog
from .error_dialog_css import STYLES


class ErrorDialog(GradientDialog):
    """
    A custom dialog that displays errors related to rules.
    It organizes errors by rule and allows the user to close the dialog after reviewing the issues.

    Args:
        errors (List[Dict[Rules]]): A list of Rule dictionaries with errors
        parent (QWidget, optional): The parent widget of the dialog. Defaults to None.

    """

    def __init__(self, errors: List[Dict[str, Any]], parent: Optional[QWidget] = None):
        """Initialize the ErrorDialog with a list of errors and optional parent widget."""

        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)

        self.setFixedHeight(450)
        self.setFixedWidth(450)
        self.setWindowTitle("Rule Errors")

        self.setStyleSheet(STYLES)

        self.settings_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WA_StyledBackground, True)
        outter_layout = WidgetFactory.create_form_box(
            "Errors",
            self.settings_layout,
            False,
            object_name="Error-Outer",
            title_color="#fcfcfc",
            title_font_size=18,
        )

        error_container = QWidget()
        error_container.setObjectName("Error-Container")
        error_container_layout = QVBoxLayout(error_container)
        error_container_layout.setSpacing(0)
        error_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        error_container.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidget(error_container)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.repaint_shadow)
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.repaint_shadow)

        outter_layout.addRow(self.scroll_area)
        outter_layout.setContentsMargins(0, 0, 0, 0)
        self.close_btn = QPushButton("Close")
        self.close_btn.setObjectName("close-btn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        outter_layout.addRow(self.close_btn)
        self.close_btn.clicked.connect(self.accept)

        for form in errors:
            if form["errors"]:

                rule_name = form["rule_name"]

                err_outter_layout = WidgetFactory.create_form_box(
                    rule_name,
                    error_container_layout,
                    False,
                    object_name="Error-Outer",
                    title_color="#fcfcfc",
                    title_font_size=16,
                )

                err_outter_layout.setVerticalSpacing(0)
                for error in form["errors"]:
                    field, path, message = SchemaValidator.format_validation_error(
                        error
                    )

                    inner_layout = WidgetFactory.create_form_box(
                        "",
                        err_outter_layout,
                        [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                        "#f58220",
                    )

                    h_layout = QHBoxLayout()

                    field_des_label = QLabel("Field:")
                    field_des_label.setMaximumWidth(37)
                    field_des_label.setObjectName("field-des-label")
                    field_name_label = QLabel(f"{field}")

                    h_layout.addWidget(field_des_label)
                    h_layout.addWidget(field_name_label)

                    h2_layout = QHBoxLayout()
                    failure_des_label = QLabel("Failure Reason:")
                    failure_des_label.setMaximumWidth(100)
                    failure_des_label.setObjectName("fail-des-label")
                    failure_msg_label = QLabel(f"{message}")

                    h2_layout.addWidget(failure_des_label)
                    h2_layout.addWidget(failure_msg_label)

                    h3_layout = QVBoxLayout()
                    h3_layout.addLayout(h_layout)
                    h3_layout.addLayout(h2_layout)
                    inner_layout.addRow(h3_layout)

    def repaint_shadow(self) -> None:
        """Repaint shadow of widget. Used for repainting shadow after the scroll bar moves

        Returns:
            None: This function does not return a value.
        """
        self.update()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event by disconnecting scroll bar signals and calling the base class close event.

        Args:
            event (QCloseEvent): The close event object.

        Returns:
            None: This function does not return a value.
        """
        try:

            self.scroll_area.verticalScrollBar().valueChanged.disconnect(
                self.repaint_shadow
            )
            self.scroll_area.horizontalScrollBar().valueChanged.disconnect(
                self.repaint_shadow
            )

        except Exception as e:
            print(e)

        super().closeEvent(event)
