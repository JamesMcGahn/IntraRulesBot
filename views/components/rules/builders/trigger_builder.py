from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory
    from .action_trigger_details_builder import ActionTriggerDetailsBuilder
from .base_builder import BaseBuilder
from services.rules.models.triggers import FrequencyTrigger, ActionTrigger


class TriggerBuilder(BaseBuilder):
    def __init__(
        self,
        field_factory: RuleFieldFactory,
        rule: Rule,
        details_builder: ActionTriggerDetailsBuilder,
    ):
        super().__init__(field_factory, rule)
        self.details_builder = details_builder

    def build(self, parent_layout: QFormLayout) -> None:

        if isinstance(self.rule.trigger, FrequencyTrigger):
            frequency_layout = self.create_box("Frequency Settings", parent_layout)

            freq_int = str(self.rule.trigger.time_interval)

            self.field_factory.text_row(
                line_edit_value=freq_int,
                label_text="Time Interval:",
                parent_layout=frequency_layout,
                full_path=self.build_path(
                    "frequency_based",
                    "time_interval",
                ),
            )
        elif isinstance(self.rule.trigger, ActionTrigger):
            action_layout = self.create_box("Action Trigger Settings", parent_layout)
            self.details_builder.build(action_layout)
