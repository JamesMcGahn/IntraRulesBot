from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from services.rules.models.agent_state import AgentState
    from services.rules.models.triggers import ActionTrigger
    from services.rules.models.triggers.action_based.action_trigger_details_base import (
        BaseActionTriggerDetails,
    )
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory
from .base_builder import BaseBuilder
from services.rules.models.triggers import ActionTrigger
from .models.details_row import DetailsRow
from services.rules.models.triggers.action_based import (
    AgentStateChangeDetails,
    AgentLoggedInDetails,
    AgentLoggedOutDetails,
    IntraQuickActionClicked,
    AgentTimeInStateDetails,
)


class ActionTriggerDetailsBuilder(BaseBuilder):
    def __init__(self, field_factory: RuleFieldFactory, rule: Rule):
        super().__init__(field_factory, rule)

    def build(self, parent_layout: QFormLayout) -> None:
        """
        Creates detail fields for the given action trigger.
        """

        trigger_layout = self.create_box(
            "Action Trigger Provider Settings", parent_layout, "detail"
        )

        self.details_dispatcher = {
            AgentStateChangeDetails: self._build_acd_state_changed,
            AgentLoggedInDetails: self._build_acd_user_logged_in,
            AgentLoggedOutDetails: self._build_acd_user_logged_out,
            IntraQuickActionClicked: self._build_intra_quick_action,
            AgentTimeInStateDetails: self._build_acd_time_in_state,
        }

        self._build_general_settings(self.rule.trigger, trigger_layout)
        details_layout = self.build_detail_box(
            self.rule.trigger.provider_condition, parent_layout
        )
        self._dispatch_build_details(self.rule.trigger.details, details_layout)

    def _dispatch_build_details(
        self, details: BaseActionTriggerDetails, parent_layout: QFormLayout
    ):
        handler = self.details_dispatcher.get(type(details))
        if handler is None:
            raise ValueError(f"No handler registered for {type(details).__name__}")
        handler(details, parent_layout)

    def _build_general_settings(
        self, trigger: ActionTrigger, parent_layout: QFormLayout
    ):
        action_based_fields = [
            DetailsRow(
                trigger.provider_category,
                "Provider Category:",
                self.build_path("action_based", "provider_category"),
            ),
            DetailsRow(
                trigger.provider_instance,
                "Provider Instance:",
                self.build_path("action_based", "provider_instance"),
            ),
            DetailsRow(
                trigger.provider_condition,
                "Provider Condition:",
                self.build_path("action_based", "provider_condition"),
            ),
        ]

        self.build_text_rows(action_based_fields, parent_layout)

    def _build_details_state(
        self, states: list[AgentState], parent_layout: QFormLayout
    ):

        state_layout = self.create_box("State", parent_layout, "detail")

        for index, state in enumerate(states):

            self.field_factory.text_row(
                line_edit_value=state.state,
                label_text="State",
                parent_layout=state_layout,
                full_path=self.build_path(
                    "action_based",
                    "details",
                    "state",
                    index,
                    "state",
                ),
            )
            self.field_factory.text_row(
                line_edit_value=state.aux,
                label_text="Aux",
                parent_layout=state_layout,
                full_path=self.build_path(
                    "action_based",
                    "details",
                    "state",
                    index,
                    "aux",
                ),
            )

    def _build_acd_state_changed(
        self, details: AgentStateChangeDetails, parent_layout: QFormLayout
    ):

        self._build_details_state(details.state, parent_layout)

        detail_fields = [
            DetailsRow(
                details.action_type,
                "Action Type:",
                self.build_path("action_based", "details", "action_type"),
            ),
            DetailsRow(
                details.equality_operator,
                "Equality Operator:",
                self.build_path("action_based", "details", "equality_operator"),
            ),
            DetailsRow(
                details.user_list,
                "User List:",
                self.build_path("action_based", "details", "user_list"),
            ),
        ]

        self.build_text_rows(detail_fields, parent_layout)

    def _build_acd_user_logged_in(
        self, details: AgentLoggedInDetails, parent_layout: QFormLayout
    ):

        detail_fields = [
            DetailsRow(
                details.action_type,
                "Action Type:",
                self.build_path("action_based", "details", "action_type"),
            ),
            DetailsRow(
                details.user_list,
                "User List:",
                self.build_path("action_based", "details", "user_list"),
            ),
        ]
        self.build_text_rows(detail_fields, parent_layout)

    def _build_acd_user_logged_out(
        self, details: AgentLoggedOutDetails, parent_layout: QFormLayout
    ):
        detail_fields = [
            DetailsRow(
                details.action_type,
                "Action Type:",
                self.build_path("action_based", "details", "action_type"),
            ),
            DetailsRow(
                details.user_list,
                "User List:",
                self.build_path("action_based", "details", "user_list"),
            ),
        ]
        self.build_text_rows(detail_fields, parent_layout)

    def _build_intra_quick_action(
        self, details: IntraQuickActionClicked, parent_layout: QFormLayout
    ):
        detail_fields = [
            DetailsRow(
                details.action_type,
                "Action Type:",
                self.build_path("action_based", "details", "action_type"),
            ),
            DetailsRow(
                details.quick_action_name,
                "Quick Action Name:",
                self.build_path("action_based", "details", "quick_action_name"),
            ),
        ]
        self.build_text_rows(detail_fields, parent_layout)

    def _build_acd_time_in_state(
        self, details: AgentTimeInStateDetails, parent_layout: QFormLayout
    ):
        self._build_details_state(details.state, parent_layout)
        detail_fields = [
            DetailsRow(
                details.action_type,
                "Action Type:",
                self.build_path("action_based", "details", "action_type"),
            ),
            DetailsRow(
                details.equality_operator,
                "Equality Operator:",
                self.build_path("action_based", "details", "equality_operator"),
            ),
            DetailsRow(
                details.aux_equality_operator,
                "Aux Equality Operator:",
                self.build_path("action_based", "details", "aux_equality_operator"),
            ),
            DetailsRow(
                str(details.equality_threshold),
                "Equality Threshold:",
                self.build_path("action_based", "details", "equality_threshold"),
            ),
            DetailsRow(
                details.user_list,
                "User List:",
                self.build_path("action_based", "details", "user_list"),
            ),
        ]
        self.build_text_rows(detail_fields, parent_layout)
