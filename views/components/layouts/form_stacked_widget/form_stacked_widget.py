from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..stacked_widget import StackedWidget


class StackedFormWidget(StackedWidget):
    def __init__(self):
        super().__init__()
        self.widget_map = {}
        self.form_factories = []

    def remove_all(self):
        while self.count() > 0:
            if len(self.form_factories) > 0:
                del self.form_factories[0]
            widget = self.widget(0)
            self.removeWidget(widget)
            widget.deleteLater()
        self.widget_map.clear()
        self.form_factories.clear()

    def add_form(self, adapter):
        """Add a widget to the stacked widget and map its name."""

        self.addWidget(adapter.widget)

        index = self.indexOf(adapter.widget)
        self.widget_map[adapter.guid] = index
        self.form_factories.append(adapter)

    def get_form_by_index(self, index):
        if not isinstance(index, int):
            return
        if index >= 0 and index <= self.count():
            return self.form_factories[index]

    def remove_form_by_index(self, index):
        if not isinstance(index, int):
            return
        if index >= 0 and index <= self.count():
            widget = self.widget(index)
            self.removeWidget(widget)
            widget.deleteLater()
            del self.form_factories[index]

    def get_form_factories(self) -> list[RuleFormManager]:
        return self.form_factories

    def get_widget_map(self):
        return self.widget_map

    def get_widget_index_by_guid(self, guid: str) -> int:
        return self.widget_map.get(guid, -1)

    def get_form_by_guid(self, guid: str):
        index = self.get_widget_index_by_guid(guid)
        print(index, self.widget_map)
        if index > -1:
            return self.get_form_by_index(index)
