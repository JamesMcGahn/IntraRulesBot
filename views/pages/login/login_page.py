from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from components.toasts import QToast
from models.login import LoginModel

from .login_page_css import STYLES
from .login_page_ui import LoginPageView


class LoginPage(QWidgetBase):
    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()

        self.setStyleSheet(STYLES)

        self.ui = LoginPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.save_btn.clicked.connect(self.save_creds)

        login_model = LoginModel()
        login_model.success.connect(self.success_save)
        self.send_creds.connect(login_model.save_creds)

        # TODO: Use Method to set values
        username, password, url, login_url = login_model.get_creds()
        self.ui.username.setText(username)
        self.ui.password.setText(password)
        self.ui.url.setText(url)
        self.ui.login_url.setText(login_url)

    # TODO: Use Method to get values
    def save_creds(self):
        if self.ui.url.text() and self.ui.url.text()[-1] != "/":
            self.ui.url.setText(self.ui.url.text() + "/")
        self.send_creds.emit(
            self.ui.username.text(),
            self.ui.password.text(),
            self.ui.url.text(),
            self.ui.login_url.text(),
        )
        self.logging("Saving Login Credentials", "INFO")

    @Slot()
    def success_save(self):
        QToast(self, "success", "Saved Successful", "Credentials Saved.")
        self.logging("Login Credentials Saved Successful", "INFO")
