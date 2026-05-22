from dataclasses import dataclass

from typing import Mapping

from ...rules.enums import ACTIONDETAILTYPE


@dataclass(frozen=True)
class ActionCommonSelectors:
    provider_category_items: str
    provider_instance_items: str
    provider_condition_items: str
    add_action_button: str


@dataclass(frozen=True)
class ActionEmailSelectors:
    email_settings_button: str
    email_subject: str
    email_message: str
    user_settings_button: str
    email_individual_radio: str
    email_address: str


ActionDetailSelectors = ActionEmailSelectors


@dataclass(frozen=True)
class ActionSelectors:
    common: ActionCommonSelectors
    details: Mapping[ACTIONDETAILTYPE, ActionDetailSelectors]
