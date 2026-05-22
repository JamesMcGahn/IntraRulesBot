from dataclasses import dataclass

from typing import Mapping

from ...rules.enums import CONDITIONDETAILTYPE


@dataclass(frozen=True)
class ConditionCommonSelectors:
    provider_category_items: str
    provider_instance_items: str
    provider_condition_items: str
    add_condition_button: str


@dataclass(frozen=True)
class ConditionStatsSelectors:
    equality_operator_dropdown_arrow: str
    equality_operator_dropdown_items: str
    equality_threshold_input: str
    queue_source_radio: str
    queue_dropdown_arrow: str
    queue_dropdown_items: str


ConditionDetailSelectors = ConditionStatsSelectors


@dataclass(frozen=True)
class ConditionSelectors:
    common: ConditionCommonSelectors
    details: Mapping[CONDITIONDETAILTYPE, ConditionDetailSelectors]
