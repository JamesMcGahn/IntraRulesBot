from PySide6.QtCore import QObject, Signal, Slot

from utils.singletons import QSingleton


class RulesModel(QObject, metaclass=QSingleton):
    data_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.rules = []

    @Slot(object)
    def add_rule(self, rule):
        self.rules.append(rule)
        self.data_changed.emit(self.rules)

    @Slot(list)
    def reset_model(self, rules):
        self.rules = rules
        self.data_changed.emit(self.rules)
