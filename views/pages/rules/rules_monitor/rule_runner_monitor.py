from typing import Optional
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QTableView,
)

from ....components.helpers import WidgetFactory
from ....components.dialogs import GradientDialog
from .monitor_table import MonitorTableModel
from services.rule_monitor.models import RuleRunRow

# from .rule_set_css import STYLES


class RuleRunnerMonitor(GradientDialog):
    """
    A custom dialog for displaying a message with a gradient background.
    """

    send_form = Signal(str, str)

    def __init__(self, parent: Optional[QWidget] = None):

        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)
        self.title = "Rule Runner Monitor"
        self.setMinimumWidth(700)
        self.setWindowTitle(self.title)
        self.message = "Msg"
        self.settings_layout = QVBoxLayout(self)
        table_font = QFont()
        table_font.setPointSize(18)
        self.monitor_table_model = MonitorTableModel()
        self.table_view_w = QTableView()
        self.table_view_w.setFont(table_font)
        self.table_view_w.setModel(self.monitor_table_model)
        # self.table_view_w.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_w.show()
        # self.setStyleSheet(STYLES)

        self.setAttribute(Qt.WA_StyledBackground, True)
        outter_layout = WidgetFactory.create_form_box(
            self.title,
            self.settings_layout,
            False,
            object_name="Error-Outer",
            title_color="#fcfcfc",
            title_font_size=18,
        )
        # self.settings_layout.addWidget(self.table_view_w)
        outter_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
        )
        inner_layout.setContentsMargins(5, 5, 5, 5)
        inner_layout.setSpacing(5)
        inner_widget = QWidget()
        inner_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        inner_widget_layout = QFormLayout(inner_widget)
        inner_widget_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        inner_layout.addRow(self.table_view_w)

        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.setObjectName("cancel-btn")

        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)
        btn_box.addWidget(self.cancel_btn)

        outter_layout.addRow(btn_box)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)

        self.cancel_btn.clicked.connect(self.handle_cancel_clicked)

    def handle_cancel_clicked(self):
        self.reject()

    def handle_upsert_row(self, row: RuleRunRow):
        self.monitor_table_model.upsert_row(row)
        self.table_view_w.resizeColumnsToContents()
