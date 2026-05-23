from PySide6.QtWidgets import QStackedWidget, QWidget


class StackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget_map: dict[str, int] = {}

    def add_widget(self, name: str, widget: QWidget):
        """Add a widget to the stacked widget and map its name."""
        self.addWidget(widget)
        index = self.indexOf(widget)
        self.widget_map[name] = index

    def get_widget_by_name(self, name: str) -> int:
        """Retrieve a widget by its name."""
        return self.widget_map.get(name)

    def set_current_by_name(self, name: str) -> None:
        index = self.widget_map.get(name)
        if index is None:
            return
        self.setCurrentIndex(index)

    def remove_by_index(self, index: int):
        if not isinstance(index, int):
            return
        if index >= 0 and index <= self.count():
            widget = self.widget(index)
            self.removeWidget(widget)
            widget.deleteLater()

    def remove_by_name(self, name: str):
        index = self.widget_map.get(name, None)
        if name is not None and index is not None:
            self.remove_by_index(index)
            del self.widget_map[name]
