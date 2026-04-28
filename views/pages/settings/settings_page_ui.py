from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from __version__ import __version__
from components.helpers import WidgetFactory


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

        outter_layout = WidgetFactory.create_form_box(
            "Application Settings",
            self.settings_layout,
            False,
            object_name="Settings-Information",
            title_color="#fcfcfc",
        )

        inner_h_layout = QHBoxLayout()

        # inner_layout = WidgetFactory.create_form_box(
        #     "Logging Settings",
        #     inner_h_layout,
        #     [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
        #     "#f58220",
        #     max_width=400,
        #     title_color="#fcfcfc",
        #     title_font_size=13,
        # )
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setTabsClosable(False)
        self.settings_layout.addWidget(self.tabs)

    def add_page_to_tab(self, tab, text, icon=None):
        if icon is None:
            icon = QIcon()
        self.tabs.addTab(tab, icon, text)
