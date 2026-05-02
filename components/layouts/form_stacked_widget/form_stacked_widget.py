from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from managers import RuleFormManager

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

    def add_form(self, rule_form: RuleFormManager, styleSheet=""):
        """Add a widget to the stacked widget and map its name."""
        rule_widget = QWidget()
        rule_widget.setContentsMargins(12, 0, 0, 0)
        rule_widget.setStyleSheet(styleSheet)

        form = rule_form.rule_form
        form.setContentsMargins(0, 0, 0, 0)
        rule_widget.setLayout(form)

        rule_widget2 = QWidget()
        rule_widget2.setContentsMargins(12, 0, 0, 0)
        rule_widget2.setStyleSheet("margin-top: 0px; padding-top: 0px;")
        h_layout = QHBoxLayout(rule_widget2)
        h_layout.addWidget(rule_widget, alignment=Qt.AlignLeft)

        self.addWidget(rule_widget2)

        index = self.indexOf(rule_widget2)
        self.widget_map[rule_form.rule_guid] = index
        self.form_factories.append(rule_form)

    def get_form_by_index(self, index) -> RuleFormManager:
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
