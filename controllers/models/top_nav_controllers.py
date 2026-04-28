from dataclasses import dataclass

from ..rules_controller import RulesController


@dataclass
class TopNavControllers:
    rules: RulesController
