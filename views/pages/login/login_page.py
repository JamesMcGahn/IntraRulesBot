from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from models.login import LoginModel

from .login_page_css import STYLES
from .login_page_ui import LoginPageView


class LoginPage(QWidgetBase):
    """
    Login page that integrates the UI view with the logic for saving credentials.

    Signals:
        send_creds (Signal[str, str, str, str]): Emitted when the user saves credentials,
            sending the username, password, base URL, and login URL to the login model.

    Attributes:
        ui (LoginPageView): The view component of the login page.
    """

    send_creds = Signal(str, str, str, str)

    def __init__(self):
        """
        Initializes the login page, connects UI components with login logic,
        and populates the fields with existing credentials if available.
        """
        super().__init__()

        self.setStyleSheet(STYLES)
        # Initialize the view
        self.ui = LoginPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.save_btn.clicked.connect(self.save_creds)
        # Initialize the login model to handle credentials
        login_model = LoginModel()
        login_model.success.connect(self.success_save)
        self.send_creds.connect(login_model.save_creds)
        # Load and set the current credentials from the model
        username, password, url, login_url = login_model.get_creds()
        self.ui.set_credentials(username, password, url, login_url)

    def save_creds(self) -> None:
        """
        Retrieves the credentials from the UI and emits the `send_creds` signal
        to save them in the login model. Logs the credential saving process.

        Returns:
            None: This function does not return a value.
        """
        username, password, url, login_url = self.ui.get_credentials()

        self.send_creds.emit(username, password, url, login_url)
        self.logging("Saving Login Credentials", "INFO")

    @Slot()
    def success_save(self):
        """
        Slot that gets called when the credentials are successfully saved.
        Displays a log message with a success toast notification.

        Returns:
            None: This function does not return a value.
        """
        self.log_with_toast(
            "Credentials Saved Successful",
            "Login Credentials Saved Successful",
            "INFO",
            "SUCCESS",
            True,
            self,
        )
