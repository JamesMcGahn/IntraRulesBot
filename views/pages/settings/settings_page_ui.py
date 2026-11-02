from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTabWidget, QLabel
from __version__ import __version__


class PageSettingsUI(QWidget):
    """
    A UI component that represents the Settings Page.
    SettingsPageView manages the UI elements for displaying and editing application settings,
    particularly related to logging configuration. It allows users to input settings, choose
    a folder for log storage, and save the configuration.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Setup the UI elements for the settings page, including the logging settings form,
        folder path selection, log file settings, and a save button.
        Connects signals for interactive components like folder selection.

        Returns:
            None: This function does not return a value.
        """
        self.settings_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setTabsClosable(False)
        self.settings_layout.addWidget(self.tabs)
        self.version = __version__
        version_label = QLabel(f"Version: {self.version}")
        version_label.setStyleSheet("color: #fcfcfc;")
        self.settings_layout.addWidget(version_label)

    def add_page_to_tab(self, tab, text, icon=None):
        if icon is None:
            icon = QIcon()
        self.tabs.addTab(tab, icon, text)
