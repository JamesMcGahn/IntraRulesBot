from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt


class RuleWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.styleSheet = self.styleSheet
        self.setContentsMargins(12, 0, 0, 0)
        self.setStyleSheet("margin-top: 0px; padding-top: 0px;")
        self.h_layout = QHBoxLayout(self)

    def add_inner_layout(self, layout, styleSheet=""):
        rule_widget = QWidget()
        rule_widget.setContentsMargins(12, 0, 0, 0)
        rule_widget.setStyleSheet(styleSheet)

        form = layout
        form.setContentsMargins(0, 0, 0, 0)
        rule_widget.setLayout(form)
        self.h_layout.addWidget(rule_widget, alignment=Qt.AlignLeft)

        return self
