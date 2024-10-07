from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from services.settings import AppSettings


class RulesModel(QObject, metaclass=QSingleton):
    data_changed = Signal(list)
    success = Signal()

    def __init__(self):
        super().__init__()
        self._rules = []
        self.settings = AppSettings()
        self.init_rules_model()

    @property
    def rules(self):
        return self._rules

    @Slot(object)
    def add_rule(self, rule):
        self._rules.append(rule)
        self.data_changed.emit(self._rules)

    @Slot(list)
    def reset_model(self, rules):
        self._rules = rules
        self.data_changed.emit(self._rules)

    @Slot(list)
    def save_rules(self, rules):
        self.settings.begin_group("rules-model")
        self.settings.set_value("rules_saved", rules)
        self._rules = rules
        self.settings.end_group()

    def init_rules_model(self):
        self.settings.begin_group("rules-model")
        self._rules = self.settings.get_value("rules_saved", [])
        self.settings.end_group()
