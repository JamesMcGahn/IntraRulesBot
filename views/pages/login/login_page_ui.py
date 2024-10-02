from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from components.buttons import GradientButton
from components.helpers import WidgetFactory


class LoginPageView(QWidget):
    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.login_layout = QVBoxLayout(self)

        outter_layout = WidgetFactory.create_form_box(
            "Login Information",
            self.login_layout,
            False,
            object_name="Login-Information",
        )

        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58321",
            max_width=400,
        )

        self.url = WidgetFactory.create_form_input_row("", "Base URL:", inner_layout)
        self.login_url = WidgetFactory.create_form_input_row(
            "", "Login URL:", inner_layout
        )
        self.username = WidgetFactory.create_form_input_row(
            "", "Username", inner_layout
        )
        self.password = WidgetFactory.create_form_input_row(
            "", "Password:", inner_layout
        )
        self.password.setEchoMode(QLineEdit.Password)
        self.save_btn = GradientButton(
            "Save",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58321",
            1,
            3,
        )

        inner_layout.addRow(self.save_btn)
        inner_layout.setAlignment(self.save_btn, Qt.AlignmentFlag.AlignRight)
