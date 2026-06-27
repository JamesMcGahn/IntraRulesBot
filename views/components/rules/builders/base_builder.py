from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory

from views.components.helpers.widget_factory import WidgetFactory


class BaseBuilder:

    def __init__(self, field_factory: RuleFieldFactory, rule: Rule):
        self.rule = rule
        self.field_factory = field_factory

    def build(self, layout: QFormLayout) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} has not implemented the build method."
        )

    def build_path(self, *parts) -> str:
        return ".".join(str(p) for p in parts)

    def create_box(self, title: str, layout: QFormLayout) -> QFormLayout:
        return WidgetFactory.create_form_box(
            title,
            layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            drop_shadow_effect=False,
            title_font_size=13,
            title_color="#fcfcfc",
        )
