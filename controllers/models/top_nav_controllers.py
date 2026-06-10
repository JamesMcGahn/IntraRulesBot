from dataclasses import dataclass

from ..rules.rules_controller import RulesController
from ..ui_controller import UIController


@dataclass
class TopNavControllers:
    rules: RulesController
    ui: UIController
