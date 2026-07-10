from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory
    from services.rules.models.conditions import (
        Condition,
        BaseConditionDetails,
        ConditionStatsDetails,
    )

from .base_builder import BaseBuilder
from .models.details_row import DetailsRow
from services.rules.models.conditions import (
    ConditionStatsDetails,
    ConditionWFMSegmentCodesDetails,
)
from services.rules.enums import SEGMENTSTARTTIME, SEGMENTTIMEINTERVAL


class ConditionsBuilder(BaseBuilder):
    def __init__(self, field_factory: RuleFieldFactory, rule: Rule):
        super().__init__(field_factory, rule)

        self.details_dispatcher = {
            ConditionStatsDetails: self._build_acd_stats,
            ConditionWFMSegmentCodesDetails: self._build_wfm_segment_codes,
        }

    def build(self, parent_layout: QFormLayout) -> None:
        """
        Adds condition fields to the form layout.
        """
        self._build_conditions(self.rule, parent_layout)

    def _build_conditions(self, rule: Rule, parent_layout: QFormLayout):
        for index, condition in enumerate(rule.conditions):
            title = condition.details.condition_type.title()

            condition_layout = self.create_box(
                f"Condition - {(index+1)} - {title}", parent_layout
            )
            self._build_general_settings(condition, index, condition_layout)
            details_box = self.build_detail_box(
                condition.provider_condition, condition_layout
            )
            self._dispatch_build_details(condition.details, index, details_box)

    def _build_general_settings(
        self, condition: Condition, condition_index: int, parent_layout: QFormLayout
    ):
        condition_layout = self.create_box(
            "Condition Provider Settings", parent_layout, "detail"
        )

        condition_fields = [
            DetailsRow(
                condition.provider_category,
                "Provider Category:",
                self.build_path("conditions", condition_index, "provider_category"),
            ),
            DetailsRow(
                condition.provider_instance,
                "Provider Instance:",
                self.build_path("conditions", condition_index, "provider_instance"),
            ),
            DetailsRow(
                condition.provider_condition,
                "Provider Condition:",
                self.build_path("conditions", condition_index, "provider_condition"),
            ),
        ]

        self.build_text_rows(condition_fields, condition_layout)

    def _dispatch_build_details(
        self,
        details: BaseConditionDetails,
        condition_index: int,
        parent_layout: QFormLayout,
    ):
        handler = self.details_dispatcher.get(type(details))
        if handler is None:
            raise ValueError(f"No handler registered for {type(details).__name__}")
        handler(details, condition_index, parent_layout)

    def _build_acd_stats(
        self,
        details: ConditionStatsDetails,
        condition_index: int,
        parent_layout: QFormLayout,
    ):

        detail_fields = [
            DetailsRow(
                details.condition_type,
                "Condition Type:",
                self.build_path(
                    "conditions", condition_index, "details", "condition_type"
                ),
            ),
            DetailsRow(
                details.equality_operator,
                "Equality Operator:",
                self.build_path(
                    "conditions", condition_index, "details", "equality_operator"
                ),
            ),
            DetailsRow(
                str(details.equality_threshold),
                "Equality Threshold:",
                self.build_path(
                    "conditions", condition_index, "details", "equality_threshold"
                ),
            ),
            DetailsRow(
                details.queues_source,
                "Queue Source:",
                self.build_path(
                    "conditions", condition_index, "details", "queues_source"
                ),
            ),
        ]
        self.build_text_rows(detail_fields, parent_layout)

    def _build_wfm_segment_codes(
        self,
        details: ConditionWFMSegmentCodesDetails,
        condition_index: int,
        parent_layout: QFormLayout,
    ):

        detail_fields = [
            DetailsRow(
                details.condition_type,
                "Condition Type:",
                self.build_path(
                    "conditions", condition_index, "details", "condition_type"
                ),
            ),
            DetailsRow(
                details.equality_operator,
                "Equality Operator:",
                self.build_path(
                    "conditions", condition_index, "details", "equality_operator"
                ),
            ),
            DetailsRow(
                ",".join(details.segment_codes),
                "Segment Codes",
                self.build_path(
                    "conditions", condition_index, "details", "segment_codes"
                ),
            ),
            DetailsRow(
                details.match_mode,
                "Match Mode:",
                self.build_path("conditions", condition_index, "details", "match_mode"),
            ),
            DetailsRow(
                details.segment_time_interval,
                "Time Interval:",
                self.build_path(
                    "conditions", condition_index, "details", "segment_time_interval"
                ),
            ),
            DetailsRow(
                details.segment_start_time,
                "Start Time:",
                self.build_path(
                    "conditions", condition_index, "details", "segment_time_interval"
                ),
            ),
        ]

        if details.segment_start_time in (
            SEGMENTSTARTTIME.RULE_RUN_MINUS,
            SEGMENTSTARTTIME.RULE_RUN_PLUS,
        ):
            detail_fields.append(
                DetailsRow(
                    str(details.segment_offset),
                    "Segment Offset:",
                    self.build_path(
                        "conditions", condition_index, "details", "segment_offset"
                    ),
                )
            )

        if details.segment_time_interval == SEGMENTTIMEINTERVAL.DURATION:
            detail_fields.append(
                DetailsRow(
                    str(details.segment_duration),
                    "Duration:",
                    self.build_path(
                        "conditions",
                        condition_index,
                        "details",
                        "segment_duration",
                    ),
                )
            )

        else:
            detail_fields.append(
                DetailsRow(
                    details.segment_end_time,
                    "End Time:",
                    self.build_path(
                        "conditions",
                        condition_index,
                        "details",
                        "segment_end_time",
                    ),
                )
            )

        detail_fields.append(
            DetailsRow(
                details.user_list,
                "User List:",
                self.build_path("conditions", condition_index, "details", "user_list"),
            ),
        )

        self.build_text_rows(detail_fields, parent_layout)
