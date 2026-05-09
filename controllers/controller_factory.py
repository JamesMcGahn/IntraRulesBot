from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from context import AppContext

from .models import (
    SettingsPageControllers,
    CentralWidgetControllers,
    RulesPageControllers,
    BookmarksPageControllers,
    TopNavControllers,
)


class ControllerFactory:
    def __init__(self, context: AppContext):
        self.ctx = context

    def create_settings_page(self) -> SettingsPageControllers:
        return SettingsPageControllers(settings=self.ctx.settings_controller)

    def create_central_widget(self) -> CentralWidgetControllers:
        return CentralWidgetControllers(
            rules=self.ctx.rules_controller,
            settings=self.ctx.settings_controller,
            rule_sets=self.ctx.rule_sets_controller,
            ui=self.ctx.ui_controller,
        )

    def create_top_nav_bar(self) -> TopNavControllers:
        return TopNavControllers(rules=self.ctx.rules_controller)

    def create_rules_page(self) -> RulesPageControllers:
        return RulesPageControllers(rules=self.ctx.rules_controller)

    def create_bookmarks_page(self) -> BookmarksPageControllers:
        return BookmarksPageControllers(rule_sets=self.ctx.rule_sets_controller)
