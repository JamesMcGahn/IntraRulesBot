from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import MainScreenControllers


from PySide6.QtCore import Signal, Slot

from base import QWidgetBase

from .main_screen_ui import MainScreenView
from views.pages import BookMarksPage, LogsPage, RulesPage, SettingsPage
from ...base.enums import PAGE


class MainScreen(QWidgetBase):
    """
    MainScreen serves as the controller for the MainScreenView. It manages
    interactions between different parts of the view, such as changing pages
    """

    close_main_window = Signal()

    def __init__(self, controllers: MainScreenControllers):
        super().__init__()
        self.ui = MainScreenView()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)
        self.setObjectName("main_screen")
        self.controllers = controllers
        self.ui_controller = controllers.ui

        # self.appshutdown.connect(self.ui.rules_page.notified_app_shutting)

        # Pages
        self.rules_page = RulesPage(controllers=self.controllers.rules_page)
        self.settings_page = SettingsPage(controllers=self.controllers.settings_page)
        self.logs_page = LogsPage()
        self.bookmarks_page = BookMarksPage(controllers=self.controllers.bookmark_page)

        # Add pages to stacked widget
        self.ui.add_page_to_stacked_widget(PAGE.EDITOR, self.rules_page)
        self.ui.add_page_to_stacked_widget(PAGE.LOG, self.logs_page)
        self.ui.add_page_to_stacked_widget(PAGE.BOOKMARK, self.bookmarks_page)
        self.ui.add_page_to_stacked_widget(PAGE.SETTINGS, self.settings_page)

        self.ui_controller.page_changed.connect(self.change_page)

        self.ui_controller.set_active_page(PAGE.EDITOR)

    @Slot(object)
    def change_page(self, page: PAGE) -> None:
        """
        Changes the page displayed in the stacked widget based on the button clicked.
        """

        if page == PAGE.EXIT:
            self.close_main_window.emit()
            return
        self.ui.stackedWidget.set_current_by_name(page)
