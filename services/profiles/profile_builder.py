from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter


from base import ServiceBase
from base.enums import INTRAVERSION


from .models import (
    ActionCommonSelectors,
    ActionSelectors,
    BrowserProfile,
    ConditionCommonSelectors,
    ConditionSelectors,
    ExecutorSelectors,
    LoginSelectors,
    ProviderInstanceSelectors,
    ProviderSelectors,
    QueueSelectors,
    RuleFormSelectors,
    TriggerCommonSelectors,
    TriggerSelectors,
    TRIGGER_MAPPING,
    CONDITION_MAPPING,
    ACTION_MAPPING,
)
from ..rules.enums import ACTIONTRIGGERDETAILTYPE, CONDITIONDETAILTYPE, ACTIONDETAILTYPE


class ProfileBuilder(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)

    def build_profile(self, profile: object) -> BrowserProfile:
        s_data = profile["selectors"]
        try:
            return BrowserProfile(
                version=INTRAVERSION(profile["version"]),
                selectors=ExecutorSelectors(
                    rule_form=self._build_rule_form(
                        s_data["rule_form"],
                    ),
                    login=self._build_login(s_data["login"]),
                    providers=self._build_providers(s_data["providers"]),
                    provider_instance=self._build_provider_instance(
                        s_data["provider_instance"]
                    ),
                    queues=self._build_queues(s_data["queues"]),
                    triggers=self._build_triggers(s_data["triggers"]),
                    conditions=self._build_conditions(s_data["conditions"]),
                    actions=self._build_actions(s_data["actions"]),
                ),
            )
        except Exception as e:
            self._logging(f"Error building profile from file: {e}", "ERROR")
            raise ValueError("Error building profile from file") from e

    def _build_rule_form(self, data):
        return RuleFormSelectors(**data)

    def _build_login(self, data):
        return LoginSelectors(**data)

    def _build_providers(self, data):
        return ProviderSelectors(**data)

    def _build_provider_instance(self, data):
        return ProviderInstanceSelectors(**data)

    def _build_queues(self, data):
        return QueueSelectors(**data)

    def _build_triggers(self, data):
        return TriggerSelectors(
            common=TriggerCommonSelectors(**data["common"]),
            details=self._build_trigger_details(data["details"]),
        )

    def _build_trigger_details(self, data):
        details = {}

        for k, v in data.items():
            detail_type = ACTIONTRIGGERDETAILTYPE(k)
            detail_class = TRIGGER_MAPPING[detail_type]

            details[detail_type] = detail_class(**v)
        return details

    def _build_conditions(self, data):
        return ConditionSelectors(
            common=ConditionCommonSelectors(**data["common"]),
            details=self._build_condition_details(data["details"]),
        )

    def _build_condition_details(self, data):
        details = {}

        for k, v in data.items():
            detail_type = CONDITIONDETAILTYPE(k)
            detail_class = CONDITION_MAPPING[detail_type]

            details[detail_type] = detail_class(**v)
        return details

    def _build_actions(self, data):
        return ActionSelectors(
            common=ActionCommonSelectors(**data["common"]),
            details=self._build_action_details(data["details"]),
        )

    def _build_action_details(self, data):
        details = {}

        for k, v in data.items():
            detail_type = ACTIONDETAILTYPE(k)
            detail_class = ACTION_MAPPING[detail_type]

            details[detail_type] = detail_class(**v)
        return details
