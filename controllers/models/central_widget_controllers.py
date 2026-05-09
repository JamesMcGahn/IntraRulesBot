from dataclasses import dataclass

from ..rules.rules_controller import RulesController
from ..rule_sets.rule_sets_controller import RuleSetsController
from ..settings_controller import SettingsController
from ..ui_controller import UIController


@dataclass
class CentralWidgetControllers:
    rules: RulesController
    rule_sets: RuleSetsController
    settings: SettingsController
    ui: UIController
