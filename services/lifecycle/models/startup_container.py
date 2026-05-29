from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...logger.adapters import LogAdapter
    from controllers.rule_sets import RuleSetsController
    from controllers.rules import RulesController
    from ...auth.session import SessionRegistry
from dataclasses import dataclass


@dataclass
class StartUpContainer:
    logger: LogAdapter
    rules_controller: RulesController
    rule_sets_controller: RuleSetsController
    session_registry: SessionRegistry
