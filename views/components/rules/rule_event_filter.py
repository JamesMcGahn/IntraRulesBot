from PySide6.QtCore import QEvent, QObject, Signal


class RuleEventFilter(QObject):
    """
    Event filter class that detects when focus enters field
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
            field_path = obj.property("field_path")
            rule_guid = obj.property("rule_guid")
            if field_path is None or rule_guid is None:
                return
            self.event_changed.emit(rule_guid, field_path)
        return super().eventFilter(obj, event)
