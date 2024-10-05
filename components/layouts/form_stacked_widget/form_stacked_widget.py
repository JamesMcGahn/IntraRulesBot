from PySide6.QtWidgets import QWidget

from managers import RuleFormManager

from ..stacked_widget import StackedWidget


class StackedFormWidget(StackedWidget):
    def __init__(self):
        super().__init__()
        self.widget_map = {}
        self.form_factories = []

    def add_form(self, rule_form: RuleFormManager):
        """Add a widget to the stacked widget and map its name."""
        rule_widget = QWidget()
        form = rule_form.rule_form
        rule_widget.setLayout(form)
        self.addWidget(rule_widget)

        index = self.indexOf(rule_widget)
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
