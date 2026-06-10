from dataclasses import dataclass

from ..rules.rules_controller import RulesController
from ..rules.rules_run_monitor_controller import RulesRunMonitorController


@dataclass
class RulesPageControllers:
    rules: RulesController
    monitor: RulesRunMonitorController
