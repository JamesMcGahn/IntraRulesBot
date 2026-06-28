from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rule_registry import RuleFieldRegistry
    from ..rule_event_filter import RuleEventFilter

from PySide6.QtWidgets import QFormLayout, QLineEdit
from PySide6.QtCore import Qt

from views.components.helpers.widget_factory import WidgetFactory


class RuleFieldFactory:

    def __init__(
        self, field_registry: RuleFieldRegistry, event_filter: RuleEventFilter
    ):
        self._field_registry = field_registry
        self._rule_guid = None
        self._event_filter = event_filter

    @property
    def rule_guid(self):
        return self._rule_guid

    @rule_guid.setter
    def rule_guid(self, guid: str):
        self._rule_guid = guid

    def _configure_event_registration(self, full_path, widget):
        widget.setProperty("field_path", full_path)
        widget.setProperty("rule_guid", self.rule_guid)
        widget.setFocusPolicy(Qt.StrongFocus)
        widget.installEventFilter(self._event_filter)

    def register_field(self, widget, full_path: str):
        self._configure_event_registration(full_path, widget)
        self._field_registry.register_field(full_path, widget)

    def text_row(
        self,
        line_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        full_path: str,
    ) -> QLineEdit:
        """
        Creates a text input row in the form and optionally updates the rule input dictionary.

        Args:
            line_edit_value (str): The initial value for the QLineEdit field.
            label_text (str): The label text for the input field.
            parent_layout (QFormLayout): The parent layout to which the row will be added.
            rule_input_path str: The path in the rule input dictionary to store the field.

        Returns:
            QLineEdit: The created QLineEdit field.
        """
        el = WidgetFactory.create_form_input_row(
            line_edit_value,
            label_text,
            parent_layout,
        )

        self.register_field(el, full_path)

        return el

    def text_edit_row(
        self,
        text_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        full_path: str,
    ) -> QLineEdit:
        el = WidgetFactory.create_form_text_edit_row(
            text_edit_value, label_text, parent_layout
        )
        self.register_field(el, full_path)

        return el
