from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import ControllerFactory

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QPushButton

from base import QWidgetBase

from .main_screen_ui import MainScreenView
from views.pages import BookMarksPage, LogsPage, RulesPage, SettingsPage
from ...base.enums import PAGE


class MainScreen(QWidgetBase):
    """
    MainScreen serves as the controller for the MainScreenView. It manages
    interactions between different parts of the view, such as changing pages and
    handling application shutdown.
    """

    close_main_window = Signal()

    def __init__(self, controller_factory: ControllerFactory):
        super().__init__()
        self.ui = MainScreenView()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)
        self.setObjectName("main_screen")
        self.controller_factory = controller_factory
        self.settings_page_controllers = self.controller_factory.create_settings_page()
        self.rules_page_controllers = self.controller_factory.create_rules_page()
        self.rule_sets_controllers = self.controller_factory.create_bookmarks_page()
        # self.appshutdown.connect(self.ui.rules_page.notified_app_shutting)

        # Pages
        self.rules_page = RulesPage(controllers=self.rules_page_controllers)
        self.settings_page = SettingsPage(controllers=self.settings_page_controllers)
        self.logs_page = LogsPage()
        self.bookmarks_page = BookMarksPage(controllers=self.rule_sets_controllers)

        # Add pages to stacked widget
        self.ui.add_page_to_stacked_widget(self.rules_page)
        self.ui.add_page_to_stacked_widget(self.logs_page)
        self.ui.add_page_to_stacked_widget(self.bookmarks_page)
        self.ui.add_page_to_stacked_widget(self.settings_page)

    @Slot(QPushButton)
    def change_page(self, btn: QPushButton) -> None:
        """
        Changes the page displayed in the stacked widget based on the button clicked.
        """
        btn_name = btn.objectName()

        if btn_name == PAGE.EDITOR:
            self.ui.stackedWidget.setCurrentIndex(0)
        elif btn_name == PAGE.LOG:
            self.ui.stackedWidget.setCurrentIndex(1)
        elif btn_name == PAGE.BOOKMARK:
            self.ui.stackedWidget.setCurrentIndex(2)
        elif btn_name == PAGE.SETTINGS:
            self.ui.stackedWidget.setCurrentIndex(3)
        elif btn_name == PAGE.EXIT:
            self.close_main_window.emit()
