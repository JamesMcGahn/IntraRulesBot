from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Rule
    from services.logger.adapters import LogAdapter
from .models.triggers import FrequencyTrigger
from .models import Rule

from .models.triggers.action_based import (
    ActionTrigger,
    AgentStateChangeDetails,
    AgentLoggedInDetails,
    AgentLoggedOutDetails,
    AgentTimeInStateDetails,
    IntraQuickActionClicked,
    SegmentOccurrenceDetails,
)
from .models.agent_state import AgentState

from .models.conditions import (
    Condition,
    ConditionStatsDetails,
    ConditionWFMSegmentCodesDetails,
)
from .models.actions import Action, ActionsEmailDetails
from .enums import ACTIONDETAILTYPE, CONDITIONDETAILTYPE, ACTIONTRIGGERDETAILTYPE

from base import ServiceBase
from base.enums import LOGLEVEL
from uuid import uuid4


class RuleBuilder(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)

        self.ACTION_DETAIL_BUILDERS = {ACTIONDETAILTYPE.EMAIL: self._build_action_email}
        self.ACTION_DETAIL_TRIGGER_BUILDERS = {
            ACTIONTRIGGERDETAILTYPE.STATE_CHANGED: self._build_action_trigger_state_changed,
            ACTIONTRIGGERDETAILTYPE.TIME_IN_STATE: self._build_action_trigger_time_in_state,
            ACTIONTRIGGERDETAILTYPE.USER_LOGGED_IN: self._build_action_trigger_user_logged_in,
            ACTIONTRIGGERDETAILTYPE.USER_LOGGED_OUT: self._build_action_trigger_user_logged_out,
            ACTIONTRIGGERDETAILTYPE.QUICK_ACTION: self._build_action_trigger_quick_action,
            ACTIONTRIGGERDETAILTYPE.SEGMENT_OCCURRENCE: self._build_action_trigger_segment_occurrence,
        }
        self.CONDITION_DETAIL_BUILDERS = {
            CONDITIONDETAILTYPE.STATS: self._build_stats_details,
            CONDITIONDETAILTYPE.SEGMENT_CODES: self._build_wfm_segment_codes,
        }

    def build_rules(self, rules) -> list[Rule]:
        return [self.build_rule(rule) for rule in rules]

    def build_rule(self, data):
        rule_name = data["rule_name"]
        guid = data.get("guid", uuid4())
        rule_category = data["rule_category"]

        if "frequency_based" in data:
            trigger = FrequencyTrigger(
                time_interval=data["frequency_based"].get("time_interval", 15)
            )
        elif "action_based" in data:
            trigger = self.build_action_trigger(data["action_based"])
        else:
            msg = "Rule must have either frequency_based or action_based trigger"
            self.logging(msg, LOGLEVEL.ERROR)
            raise ValueError(msg)
        conditions = [self.build_condition(c) for c in data["conditions"]]
        actions = [self.build_action(a) for a in data["actions"]]
        return Rule(
            rule_name=rule_name,
            guid=guid,
            rule_category=rule_category,
            trigger=trigger,
            conditions=conditions,
            actions=actions,
        )

    # TRIGGERS
    def build_action_trigger(self, data):
        return ActionTrigger(
            provider_category=data["provider_category"],
            provider_instance=data["provider_instance"],
            provider_condition=data["provider_condition"],
            details=self._build_action_trigger_details(data["details"]),
        )

    # CONDITIONS
    def build_condition(self, data):
        return Condition(
            provider_category=data["provider_category"],
            provider_instance=data["provider_instance"],
            provider_condition=data["provider_condition"],
            details=self._build_condition_details(data["details"]),
        )

    # ACTIONS
    def build_action(self, data):
        return Action(
            provider_category=data["provider_category"],
            provider_instance=data["provider_instance"],
            provider_condition=data["provider_condition"],
            details=self._build_action_details(data["details"]),
        )

    # ACTION TRIGGER BUILDERS

    def _build_action_trigger_details(self, data_detail):
        action_type = data_detail["action_type"]
        builder = self.ACTION_DETAIL_TRIGGER_BUILDERS.get(action_type)
        if not builder:
            msg = f"Unknown action_type: {action_type}"
            self.logging(msg, LOGLEVEL.ERROR)
            raise ValueError(msg)
        return builder(data_detail)

    def _build_action_trigger_state_changed(self, data_detail):
        state = []
        for state_obj in data_detail["state"]:
            state.append(AgentState(state=state_obj["state"], aux=state_obj["aux"]))
        return AgentStateChangeDetails(
            action_type=ACTIONTRIGGERDETAILTYPE(data_detail["action_type"]),
            equality_operator=data_detail["equality_operator"],
            state=state,
            user_list=data_detail["user_list"],
        )

    def _build_action_trigger_time_in_state(self, data_detail):
        state = []
        for state_obj in data_detail["state"]:
            state.append(AgentState(state=state_obj["state"], aux=state_obj["aux"]))
        return AgentTimeInStateDetails(
            action_type=ACTIONTRIGGERDETAILTYPE(data_detail["action_type"]),
            equality_operator=data_detail["equality_operator"],
            equality_threshold=data_detail["equality_threshold"],
            state=state,
            user_list=data_detail["user_list"],
            aux_equality_operator=data_detail["aux_equality_operator"],
        )

    def _build_action_trigger_user_logged_in(self, data_detail):
        return AgentLoggedInDetails(
            action_type=ACTIONTRIGGERDETAILTYPE(data_detail["action_type"]),
            user_list=data_detail["user_list"],
        )

    def _build_action_trigger_user_logged_out(self, data_detail):
        return AgentLoggedOutDetails(
            action_type=ACTIONTRIGGERDETAILTYPE(data_detail["action_type"]),
            user_list=data_detail["user_list"],
        )

    def _build_action_trigger_quick_action(self, data_detail):
        return IntraQuickActionClicked(
            action_type=ACTIONTRIGGERDETAILTYPE(data_detail["action_type"]),
            quick_action_name=data_detail["quick_action_name"],
        )

    def _build_action_trigger_segment_occurrence(self, data_detail):
        return SegmentOccurrenceDetails(
            action_type=ACTIONTRIGGERDETAILTYPE(data_detail["action_type"]),
            segment_codes=data_detail["segment_codes"],
            lookup_operator=data_detail["lookup_operator"],
            segment_lookup=data_detail["segment_lookup"],
            lead_time=data_detail["lead_time"],
            user_list=data_detail["user_list"],
        )

    # CONDITIONS
    def _build_condition_details(self, data_detail):
        condition_type = data_detail["condition_type"]
        builder = self.CONDITION_DETAIL_BUILDERS.get(condition_type)
        if not builder:
            msg = f"Unknown condition_type: {condition_type}"
            self.logging(msg, LOGLEVEL.ERROR)
            raise ValueError(msg)
        return builder(data_detail)

    def _build_stats_details(self, data_detail):
        return ConditionStatsDetails(
            condition_type=CONDITIONDETAILTYPE(data_detail["condition_type"]),
            equality_operator=data_detail["equality_operator"],
            equality_threshold=data_detail["equality_threshold"],
            queues_source=data_detail["queues_source"],
        )

    def _build_wfm_segment_codes(self, data_detail: object):
        return ConditionWFMSegmentCodesDetails(
            condition_type=CONDITIONDETAILTYPE(data_detail["condition_type"]),
            equality_operator=data_detail["equality_operator"],
            match_mode=data_detail["match_mode"],
            segment_time_interval=data_detail["segment_time_interval"],
            segment_start_time=data_detail["segment_start_time"],
            segment_occurrence=data_detail["segment_occurrence"],
            segment_codes=data_detail["segment_codes"],
            segment_offset=data_detail.get("segment_offset", None),
            segment_end_time=data_detail.get("segment_end_time", None),
            segment_duration=data_detail.get("segment_duration", None),
            user_list=data_detail["user_list"],
        )

    # ACTION BUILDERS

    def _build_action_details(self, data_detail):
        action_type = data_detail["action_type"]
        builder = self.ACTION_DETAIL_BUILDERS.get(action_type)
        if not builder:
            msg = f"Unknown action_type: {action_type}"
            self.logging(msg, LOGLEVEL.ERROR)
            raise ValueError(msg)
        return builder(data_detail)

    def _build_action_email(self, data_detail):
        return ActionsEmailDetails(
            action_type=ACTIONDETAILTYPE(data_detail["action_type"]),
            email_address=data_detail["email_address"],
            email_body=data_detail["email_body"],
            email_subject=data_detail["email_subject"],
        )
