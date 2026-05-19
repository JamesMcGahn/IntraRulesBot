from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation.models import SchemaError
    from .rule_registry import RuleFieldRegistry

from typing import Tuple

from PySide6.QtWidgets import QLineEdit, QTextEdit, QWidget

from services.validator import ValidationError


class RuleAdapter:
    """
    A manager for handling rule forms, including creation, validation, and managing input fields.


    """

    def __init__(
        self,
        guid: str,
        widget: QWidget,
        field_registry: RuleFieldRegistry,
        int_keys: Tuple[str] = ("time_interval", "equality_threshold"),
    ):
        super().__init__()

        self._guid = guid

        self._widget = widget
        self._field_registry = field_registry
        self.int_keys = int_keys

    @property
    def field_registry(self) -> RuleFieldRegistry:
        return self._field_registry

    @property
    def widget(self) -> QWidget:

        return self._widget

    @property
    def guid(self) -> str:
        """
        Returns the GUID of the rule.

        Returns:
            str: The GUID of the rule.
        """
        return self._guid

    @property
    def field_map(self) -> dict:
        """
        Returns the dictionary of rule input fields.

        Returns:
            dict: A dictionary mapping input fields to their corresponding form fields.
        """
        return self._field_registry.field_map

    def highlight_errors(self, rule_errors: list[SchemaError]) -> None:
        """
        Highlights form fields that have validation errors.

        Args:
            rule (dict): The rule input fields that will be highlighted.

        Returns:
            None: This function does not return a value.
        """
        rule_imports = self.field_map
        print(rule_imports)

        def set_sheet(el, status=False):
            if status:
                color = "green"
            else:
                color = "red"
            print(el)
            el.setStyleSheet(f"border: 1px solid {color};")

        def turn_green(field_refs):
            if isinstance(field_refs, ValidationError):
                return
            # print(field_refs)
            for key, field in field_refs.items():
                if key == "guid":
                    continue
                if isinstance(field, dict):
                    turn_green(field)
                elif isinstance(field, list):
                    for list_item in field:
                        turn_green(list_item)
                else:
                    set_sheet(field, status=True)

        turn_green(rule_imports)

        def get_value_from_path(data, path):
            current = data

            for key in path:
                try:
                    current = current[key]
                except Exception as e:
                    print(e)
            return current

        for error in rule_errors:
            element = get_value_from_path(rule_imports, error.error_path)
            if element is not None:
                set_sheet(element)

    def to_validation_dict(self) -> dict:
        """
        Creates a dictionary from the form inputs, converting fields to the appropriate types (e.g. string, int).

        Args:
            int_keys (Tuple[str]): Keys that should be converted to integers from input fields.

        Returns:
            dict: A dictionary representing the form input data.
        """
        int_keys = self.int_keys

        def make_rule_dict(field_refs, int_keys):
            x = {}
            if isinstance(field_refs, ValidationError):
                return
            for key, field in field_refs.items():
                if isinstance(field, dict):
                    x[key] = make_rule_dict(field, int_keys)
                elif isinstance(field, list):
                    x[key] = [make_rule_dict(item, int_keys) for item in field]
                else:
                    if key in int_keys:
                        if field.text().isdigit():
                            x[key] = int(field.text())
                        else:
                            x[key] = field.text()
                    elif isinstance(field, QLineEdit):
                        x[key] = field.text()
                    elif isinstance(field, QTextEdit):
                        x[key] = field.toPlainText()
            return x

        return make_rule_dict(self.field_map, int_keys)
