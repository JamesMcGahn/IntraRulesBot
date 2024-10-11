from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtWidgets import QLineEdit, QTextEdit


class EventFilter(QObject):
    event_changed = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.current_object_name = None
        self.current_object_text = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            if isinstance(obj, (QLineEdit, QTextEdit)):
                self.current_object_name = obj.objectName()
                self.current_object_text = obj.text()
                self.event_changed.emit(
                    self.current_object_name, self.current_object_text
                )
        return super().eventFilter(obj, event)
