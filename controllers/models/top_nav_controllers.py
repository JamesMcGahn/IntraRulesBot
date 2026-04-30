from dataclasses import dataclass

from ..rules.rules_controller import RulesController


@dataclass
class TopNavControllers:
    rules: RulesController
