from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory
    from services.rules.models.actions import (
        Action,
        BaseActionDetails,
    )

from .base_builder import BaseBuilder
from .models.details_row import DetailsRow
from services.rules.models.actions import ActionsEmailDetails


class ActionsBuilder(BaseBuilder):
    def __init__(self, field_factory: RuleFieldFactory, rule: Rule):
        super().__init__(field_factory, rule)

        self.details_dispatcher = {ActionsEmailDetails: self._build_comm_stats}

    def build(self, parent_layout: QFormLayout) -> None:
        """
        Adds condition fields to the form layout.
        """
        self._build_actions(self.rule, parent_layout)

    def _build_actions(self, rule: Rule, parent_layout: QFormLayout):
        for index, action in enumerate(rule.actions):
            title = action.details.action_type.title()

            action_layout = self.create_box(
                f"Action - {(index+1)} - {title}", parent_layout
            )
            self._build_general_settings(action, index, action_layout)
            details_box = self.build_detail_box(
                action.provider_condition, action_layout
            )
            self._dispatch_build_details(action.details, index, details_box)

    def _build_general_settings(
        self, action: Action, action_index: int, parent_layout: QFormLayout
    ):
        action_layout = self.create_box(
            "Action Provider Settings", parent_layout, "detail"
        )

        action_fields = [
            DetailsRow(
                action.provider_category,
                "Provider Category:",
                self.build_path("actions", action_index, "provider_category"),
            ),
            DetailsRow(
                action.provider_instance,
                "Provider Instance:",
                self.build_path("actions", action_index, "provider_instance"),
            ),
            DetailsRow(
                action.provider_condition,
                "Provider Instance:",
                self.build_path("actions", action_index, "provider_condition"),
            ),
        ]

        self.build_text_rows(action_fields, action_layout)

    def _dispatch_build_details(
        self,
        details: BaseActionDetails,
        action_index: int,
        parent_layout: QFormLayout,
    ):
        handler = self.details_dispatcher.get(type(details))
        if handler is None:
            raise ValueError(f"No handler registered for {type(details).__name__}")
        handler(details, action_index, parent_layout)

    def _build_comm_stats(
        self,
        details: ActionsEmailDetails,
        action_index: int,
        parent_layout: QFormLayout,
    ):
        detail_fields = [
            DetailsRow(
                details.action_type,
                "Action Type:",
                self.build_path("actions", action_index, "details", "action_type"),
            ),
            DetailsRow(
                details.email_subject,
                "Email Subject:",
                self.build_path("actions", action_index, "details", "email_subject"),
            ),
            DetailsRow(
                details.email_address,
                "To Email Address:",
                self.build_path("actions", action_index, "details", "email_address"),
            ),
        ]
        self.build_text_rows(detail_fields, parent_layout)

        self.field_factory.text_edit_row(
            str(details.email_body),
            "Email Body:",
            parent_layout,
            self.build_path(
                "actions",
                action_index,
                "details",
                "email_body",
            ),
        )
