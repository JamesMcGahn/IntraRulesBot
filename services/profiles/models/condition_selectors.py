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


@dataclass(frozen=True)
class ConditionWFMSegmentCodes:
    equality_operator_dropdown_arrow: str
    equality_operator_dropdown_items: str
    segment_code_dropdown_arrow: str
    segment_code_dropdown_items: str
    match_mode_any_radio: str
    match_mode_all_radio: str
    time_interval_duration_radio: str
    time_interval_start_end_radio: str
    start_time_dropdown_arrow: str
    start_time_dropdown_items: str
    duration_input: str
    segment_occurrence_dropdown_arrow: str
    segment_occurrence_dropdown_items: str
    end_time_dropdown_arrow: str
    end_time_dropdown_items: str
    user_list_arrow: str
    user_list_items: str


ConditionDetailSelectors = ConditionStatsSelectors | ConditionWFMSegmentCodes


@dataclass(frozen=True)
class ConditionSelectors:
    common: ConditionCommonSelectors
    details: Mapping[CONDITIONDETAILTYPE, ConditionDetailSelectors]
