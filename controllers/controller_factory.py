from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from context import AppContext

from .models import (
    BookmarksPageControllers,
    CentralWidgetControllers,
    MainScreenControllers,
    RulesPageControllers,
    SettingsPageControllers,
    TopNavControllers,
)


class ControllerFactory:
    def __init__(self, context: AppContext):
        self.ctx = context

    def create_central_widget(self) -> CentralWidgetControllers:
        return CentralWidgetControllers(
            main_screen=self.create_main_screen(),
            top_nav=self.create_top_nav_bar(),
            ui=self.ctx.ui_controller,
        )

    def create_top_nav_bar(self) -> TopNavControllers:
        return TopNavControllers(
            rules=self.ctx.rules_controller,
            ui=self.ctx.ui_controller,
        )

    def create_rules_page(self) -> RulesPageControllers:
        return RulesPageControllers(rules=self.ctx.rules_controller)

    def create_bookmarks_page(self) -> BookmarksPageControllers:
        return BookmarksPageControllers(rule_sets=self.ctx.rule_sets_controller)

    def create_settings_page(self) -> SettingsPageControllers:
        return SettingsPageControllers(settings=self.ctx.settings_controller)

    def create_main_screen(self) -> MainScreenControllers:
        return MainScreenControllers(
            bookmark_page=self.create_bookmarks_page(),
            rules_page=self.create_rules_page(),
            settings_page=self.create_settings_page(),
            ui=self.ctx.ui_controller,
        )
