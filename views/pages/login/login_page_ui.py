from typing import Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from components.buttons import GradientButton
from components.helpers import WidgetFactory


class LoginPageView(QWidget):
    """
    View class for the login page, providing UI components for user credential input.

    Signals:
        send_creds (Signal[str, str, str, str]): Emitted when the credentials are submitted,
            sending the base URL, login URL, username, and password.

    Attributes:
        url (QLineEdit): Input field for the base URL.
        login_url (QLineEdit): Input field for the login URL.
        username (QLineEdit): Input field for the username.
        password (QLineEdit): Input field for the password.
        save_btn (GradientButton): Button to save and submit the credentials.
    """

    send_creds = Signal(str, str, str, str)

    def __init__(self):
        """
        Initializes the login page view, sets up the UI layout and components.
        """
        super().__init__()
        self.init_ui()

    def set_credentials(
        self, username: str, password: str, url: str, login_url: str
    ) -> None:
        """
        Sets the login credentials in the input fields.

        Args:
            username (str): The username to set in the input field.
            password (str): The password to set in the input field.
            url (str): The base URL to set in the input field.
            login_url (str): The login URL to set in the input field.

        Returns:
            None: This function does not return a value.
        """
        self.username.setText(username)
        self.password.setText(password)
        self.url.setText(url)
        self.login_url.setText(login_url)

    def get_credentials(self) -> Tuple[str, str, str, str]:
        """
        Retrieves the login credentials from the input fields.

        Returns:
            Tuple[str, str, str, str]: A tuple containing the username, password, base URL, and login URL.
        """
        if self.url.text() and self.url.text()[-1] != "/":
            self.url.setText(self.url.text() + "/")

        return (
            self.username.text(),
            self.password.text(),
            self.url.text(),
            self.login_url.text(),
        )

    def init_ui(self) -> None:
        """
        Sets up the UI layout and components for the login page.
        """
        self.login_layout = QVBoxLayout(self)
        # Outer layout for the form
        outter_layout = WidgetFactory.create_form_box(
            "Login Information",
            self.login_layout,
            False,
            object_name="Login-Information",
            title_color="#fcfcfc",
        )
        # Inner layout to center the input fields
        inner_h_layout = QHBoxLayout()
        # Inner layout for the actual form inputs
        inner_layout = WidgetFactory.create_form_box(
            "",
            inner_h_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            max_width=400,
        )

        inner_h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        outter_layout.addRow(inner_h_layout)
        # Creating form input fields
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
        # Save button for submitting the form
        self.save_btn = GradientButton(
            "Save",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        # Align inner layout components
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        inner_layout.addRow(self.save_btn)
        inner_layout.setAlignment(self.save_btn, Qt.AlignmentFlag.AlignRight)
