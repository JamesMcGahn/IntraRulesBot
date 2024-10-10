import keyring
from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from services.settings import AppSettings


class LoginModel(QObject, metaclass=QSingleton):
    creds_changed = Signal(str, str, str, str)
    success = Signal()

    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.url = None
        self.login_url = None
        self.service_name = "IntraRulesBot"
        self.settings = AppSettings()
        self.init_creds()

    def get_creds(self):
        return (self.username, self.password, self.url, self.login_url)

    @Slot(str, str, str, str)
    def save_creds(self, username, password, url, login_url):
        self.username = username or None
        self.password = password or None
        self.url = url or None
        self.login_url = login_url or None

        keyring.set_password(self.service_name, self.username, self.password)
        self.settings.begin_group("login")
        self.settings.set_value("url", self.url)
        self.settings.set_value("login_url", self.login_url)
        self.settings.set_value("username", self.username)
        self.settings.end_group()

        self.creds_changed.emit(self.username, self.password, self.url, self.login_url)
        self.success.emit()

    def init_creds(self):
        self.settings.begin_group("login")
        self.url = self.settings.get_value("url", None)
        self.username = self.settings.get_value("username", None)
        self.login_url = self.settings.get_value("login_url", None)
        self.settings.end_group()
        if self.username is not None:
            self.password = keyring.get_password(self.service_name, self.username)
