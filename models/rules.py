from PySide6.QtCore import QObject, Signal


class DataModel(QObject):
    data_changed = Signal()

    def __init__(self):
        super().__init__()
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)
        self.data_changed.emit()
