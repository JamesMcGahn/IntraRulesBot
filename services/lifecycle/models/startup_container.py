from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...logger.adapters import LogAdapter
    from controllers.rule_sets import RuleSetsController
    from controllers.rules import RulesController
    from ...auth.session.session_registry import SessionRegistry
    from services.intra.v11 import IntraTokenService
    from services.settings import SettingsService
    from controllers import ProfilesController
from dataclasses import dataclass


@dataclass
class StartUpContainer:
    logger: LogAdapter
    rules_controller: RulesController
    rule_sets_controller: RuleSetsController
    session_registry: SessionRegistry
    intra_token_service: IntraTokenService
    settings_manager: SettingsService
    profiles_controller: ProfilesController
