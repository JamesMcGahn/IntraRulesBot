from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtWidgets import QLineEdit, QTextEdit


class EventFilter(QObject):
    """
    Event filter class that detects when focus enters a QLineEdit or QTextEdit widget
    and emits a signal with the widget's name and current text.

    Attributes:
        current_object_name (str or None): The name of the currently focused widget.
        current_object_text (str or None): The text content of the currently focused widget.

    Signals:
        event_changed (Signal[str, str]): Emitted when the focus enters a QLineEdit or QTextEdit,
                                          providing the widget's object name and its text content.
    """

    event_changed = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.current_object_name = None
        self.current_object_text = None

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Filters events to detect when focus enters a QLineEdit or QTextEdit widget.
        Emits the event_changed signal with the widget's object name and text content.

        Args:
            obj (QObject): The object that the event applies to.
            event (QEvent): The event being filtered.

        Returns:
            bool: True if the event is handled, False otherwise.
        """
        if event.type() == QEvent.FocusIn:
            if isinstance(obj, (QLineEdit, QTextEdit)):
                self.current_object_name = obj.objectName()
                self.current_object_text = obj.text()
                self.event_changed.emit(
                    self.current_object_name, self.current_object_text
                )
        return super().eventFilter(obj, event)
