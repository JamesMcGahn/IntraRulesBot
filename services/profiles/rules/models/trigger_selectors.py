from dataclasses import dataclass

from typing import Mapping

from ....rules.enums import ACTIONTRIGGERDETAILTYPE


@dataclass(frozen=True)
class TriggerCommonSelectors:
    provider_category_items: str
    provider_instance_items: str
    provider_condition_items: str
    add_event_trigger_button: str
    frequency_dropdown_arrow: str
    frequency_dropdown_list: str


@dataclass(frozen=True)
class TriggerStateChangedSelectors:
    state_dropdown_arrow: str
    state_dropdown_items: str
    aux_input: str
    add_state_button: str
    equal_to_radio: str
    not_equal_to_radio: str
    user_list_arrow: str
    user_list_items: str


@dataclass(frozen=True)
class TriggerUserLoggedInSelectors:
    user_list_arrow: str
    user_list_items: str


TriggerDetailSelectors = TriggerStateChangedSelectors | TriggerUserLoggedInSelectors


@dataclass(frozen=True)
class TriggerSelectors:
    common: TriggerCommonSelectors
    details: Mapping[ACTIONTRIGGERDETAILTYPE, TriggerDetailSelectors]
