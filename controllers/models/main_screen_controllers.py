from dataclasses import dataclass

from ..ui_controller import UIController
from .bookmarks_page_controllers import BookmarksPageControllers
from .rules_page_controllers import RulesPageControllers
from .settings_page_controllers import SettingsPageControllers


@dataclass
class MainScreenControllers:
    bookmark_page: BookmarksPageControllers
    rules_page: RulesPageControllers
    settings_page: SettingsPageControllers
    ui: UIController
