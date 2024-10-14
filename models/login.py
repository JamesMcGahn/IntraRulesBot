import platform
import sys
from typing import Tuple

import keyring
from keyring import get_keyring
from PySide6.QtCore import Signal, Slot

from base import QObjectBase, QSingleton
from services.settings import AppSettings


class LoginModel(QObjectBase, metaclass=QSingleton):
    """
    Manages the login credentials for the application, handling saving, retrieval,
    and secure storage of username and password using keyring.

    Attributes:
        username (str or None): The username for login.
        password (str or None): The password for login, securely stored in keyring.
        url (str or None): The main URL for the login service.
        login_url (str or None): The URL endpoint for the login action.
        service_name (str): The service name used in keyring for storing credentials.
        settings (AppSettings): The application settings instance for persistent storage.

    Signals:
        creds_changed (Signal): Emitted when credentials are successfully saved.
        success (Signal): Emitted after credentials are saved successfully.
    """

    creds_changed = Signal(str, str, str, str)
    success = Signal()

    def __init__(self):
        """
        Initializes the LoginModel with default values and loads saved credentials.
        Sets up the keyring backend based on the operating system and retrieves
        stored credentials from the application settings and keyring if available.
        """
        super().__init__()
        self.username = None
        self.password = None
        self.url = None
        self.login_url = None
        self.service_name = "IntraRulesBot"
        self.settings = AppSettings()
        self.set_keyring_backend()
        self.init_creds()

    def set_keyring_backend(self) -> None:
        """
        Configures the keyring backend based on the operating system. Windows and macOS
        have specific keyring backends set. Logs the current keyring backend or errors
        during setup.
        """
        try:
            get_keyring()
            self.logging("Current Keyring method: " + str(get_keyring()), "INFO")
            current_os = platform.system()

            if current_os == "Windows":
                keyring.core.set_keyring(
                    keyring.core.load_keyring(
                        "keyring.backends.Windows.WinVaultKeyring"
                    )
                )
                self.logging("Windows keyring backend set successfully.", "INFO")

            elif current_os == "Darwin":
                # Set the macOS Keychain as the backend
                keyring.core.set_keyring(
                    keyring.core.load_keyring("keyring.backends.macOS.Keyring")
                )
                self.logging("macOS keyring backend set successfully.", "INFO")

            else:
                self.logging(
                    "Unsupported operating system or no suitable backend found.",
                    "ERROR",
                )

        except Exception as e:
            self.logging(f"Error setting keyring backend: {e}", "ERROR")

    def get_creds(self) -> Tuple[str, str, str, str]:
        """
        Retrieves the stored credentials, including username, password, URL, and login URL.

        Returns:
            Tuple: Contains username, password, URL, and login URL.
        """
        return (self.username, self.password, self.url, self.login_url)

    @Slot(str, str, str, str)
    def save_creds(
        self, username: str, password: str, url: str, login_url: str
    ) -> None:
        """
        Saves the provided credentials to both keyring and application settings.
        Emits creds_changed signal when the credentials are updated and success signal
        once the save operation is complete.

        Args:
            username (str): The username for login.
            password (str): The password for login.
            url (str): The main URL for the login service.
            login_url (str): The URL endpoint for the login action.

        Returns:
            None: This function does not return a value.
        """
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

    def init_creds(self) -> None:
        """
        Initializes the credentials by loading them from application settings and keyring.
        If a username is found in settings, attempts to retrieve the corresponding password
        from keyring.
        """
        self.settings.begin_group("login")
        self.url = self.settings.get_value("url", None)
        self.username = self.settings.get_value("username", None)
        self.login_url = self.settings.get_value("login_url", None)
        self.settings.end_group()
        if self.username is not None:
            self.password = keyring.get_password(self.service_name, self.username)
