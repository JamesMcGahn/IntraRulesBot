from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Rule

from .models.triggers import FrequencyTrigger
from .models.triggers.action_based import ActionTrigger
from .models import Rule

from .models.triggers.action_based import ActionTrigger, AgentStateChangeDetails
from .models.agent_state import AgentState

from .models.conditions import Condition, ConditionStatsDetails
from .models.actions import Action, ActionsEmailDetails


from base import QObjectBase
from base.enums import LOGLEVEL


class RuleBuilder(QObjectBase):

    def __init__(self):
        super().__init__()

        self.ACTION_DETAIL_BUILDERS = {"email": self._build_action_email}
        self.ACTION_DETAIL_TRIGGER_BUILDERS = {
            "state": self._build_action_trigger_change_state
        }
        self.CONDITION_DETAIL_BUILDERS = {"stats": self._build_stats_details}

    def build_rules(self, rules) -> list[Rule]:
        return [self.build_rule(rule) for rule in rules]

    def build_rule(self, data):
        rule_name = data["rule_name"]
        guid = data["guid"]
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
            condtions=conditions,
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

    def _build_action_trigger_change_state(self, data_detail):
        state = []
        for state_obj in data_detail["state"]:
            state.append(AgentState(state=state_obj["state"], aux=state_obj["aux"]))
        return AgentStateChangeDetails(
            equality_operator=data_detail["equality_operator"],
            state=state,
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
            equality_operator=data_detail["equality_operator"],
            equality_threshold=data_detail["equality_threshold"],
            queues_source=data_detail["queues_source"],
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
            email_address=data_detail["email_address"],
            email_body=data_detail["email_body"],
            email_subject=data_detail["email_subject"],
        )
