from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from managers import RuleFormManager

from ..stacked_widget import StackedWidget


class StackedFormWidget(StackedWidget):
    def __init__(self):
        super().__init__()
        self.widget_map = {}
        self.form_factories = []

    def add_form(self, rule_form: RuleFormManager, styleSheet=""):
        """Add a widget to the stacked widget and map its name."""
        rule_widget = QWidget()
        rule_widget.setContentsMargins(0, 0, 0, 0)
        rule_widget.setStyleSheet(styleSheet)

        form = rule_form.rule_form
        rule_widget.setLayout(form)

        rule_widget2 = QWidget()
        rule_widget2.setContentsMargins(0, 0, 0, 0)
        rule_widget2.setStyleSheet("margin-top: 0px; padding-top: 0px;")
        h_layout = QHBoxLayout(rule_widget2)
        h_layout.addWidget(rule_widget, alignment=Qt.AlignLeft)

        self.addWidget(rule_widget2)

        index = self.indexOf(rule_widget2)
        self.widget_map[rule_form.rule_guid] = index
        self.form_factories.append(rule_form)

    def remove_form_by_index(self, index):
        if not isinstance(index, int):
            return
        if index >= 0 and index <= self.count():
            widget = self.widget(index)
            self.removeWidget(widget)
            widget.deleteLater()
            del self.form_factories[index]

    def get_form_factories(self):
        return self.form_factories

    def get_widget_map(self):
        return self.widget_map
