from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory
from .base_builder import BaseBuilder


class GeneralSettingsBuilder(BaseBuilder):
    def __init__(self, field_factory: RuleFieldFactory, rule: Rule):
        super().__init__(field_factory, rule)

    def build(self, parent_layout: QFormLayout) -> None:
        """
        Adds general settings fields to the form layout.
        """
        layout = self.create_box("General Settings", parent_layout)

        self.field_factory.text_row(
            line_edit_value=self.rule.rule_name,
            label_text="Rule Name:",
            parent_layout=layout,
            full_path="rule_name",
        )

        self.field_factory.text_row(
            line_edit_value=self.rule.rule_category,
            label_text="Rule Category:",
            parent_layout=layout,
            full_path="rule_category",
        )
