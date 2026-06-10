from PySide6.QtWidgets import QComboBox, QLineEdit, QTextEdit


class FieldRegistry:

    def __init__(self):
        self._registry = {}

    def register_field(self, key, value):
        self._registry[key] = value

    def get_all(self):
        return self._registry

    def get_field(self, key):
        if key not in self._registry:
            raise ValueError("No such key in registry.")
        else:
            return self._registry[key]

    def get_text_value(self, key):
        if key not in self._registry:
            raise ValueError("No such key in registry.")

        widget = self.get_field(key)

        if isinstance(widget, QLineEdit):
            return widget.text()

        if isinstance(widget, QTextEdit):
            return widget.toPlainText()

        if isinstance(widget, QComboBox):
            return widget.currentText()

        raise TypeError(
            f"Widget type {type(widget)} is not supported by get_text_value()"
        )

    def set_text_value(self, key, value):
        if key not in self._registry:
            raise ValueError("No such key in registry.")

        widget = self.get_field(key)

        if isinstance(widget, QLineEdit):
            return widget.setText(value)

        if isinstance(widget, QTextEdit):
            return widget.setPlainText(value)

        if isinstance(widget, QComboBox):
            return widget.setCurrentText(value)

        raise TypeError(
            f"Widget type {type(widget)} is not supported by get_text_value()"
        )
