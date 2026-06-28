from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from PySide6.QtWidgets import QFormLayout
    from ..fields.rule_field_factory import RuleFieldFactory
    from .models.details_row import DetailsRow
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

    def build_text_rows(
        self, detail_fields: list[DetailsRow], parent_layout: QFormLayout
    ):
        for field in detail_fields:
            self.field_factory.text_row(
                line_edit_value=field.initial_value,
                label_text=field.label_text,
                parent_layout=parent_layout,
                full_path=field.rule_input_path,
            )

    def build_detail_box(self, title: str, parent_layout: QFormLayout) -> QFormLayout:
        return self.create_box(f"{title} Settings", parent_layout, "detail")

    def create_box(
        self, title: str, layout: QFormLayout, style: str = "default"
    ) -> QFormLayout:

        match style:
            case "detail":
                return WidgetFactory.create_form_box(
                    title,
                    layout,
                    False,
                    object_name="Condition-Stats",
                    drop_shadow_effect=False,
                    title_font_size=11,
                )
            case _:
                return WidgetFactory.create_form_box(
                    title,
                    layout,
                    [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                    "#f58220",
                    drop_shadow_effect=False,
                    title_font_size=13,
                    title_color="#fcfcfc",
                )
