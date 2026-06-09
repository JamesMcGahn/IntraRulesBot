from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
    QSpacerItem,
)

from services.monitor.rule_monitor.models import RuleRunRow
from services.monitor.models import RunSummary
from base.events import MonitorSnapShotEvent
from ....components.dialogs import GradientDialog
from ....components.helpers import WidgetFactory
from ....components.buttons import GradientButton
from .monitor_table import MonitorTableModel
from .rule_runner_monitor_styles import STYLES
from ....base.enums.monitor_event import MONITOREVENT


class RuleRunnerMonitor(GradientDialog):
    """
    A custom dialog for displaying a message with a gradient background.
    """

    monitor_action = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):

        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)
        self.title = "Rule Runner Monitor"
        self.setMinimumWidth(700)
        self.setMaximumWidth(1500)
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
        self.setStyleSheet(STYLES)

        self.setAttribute(Qt.WA_StyledBackground, True)
        outter_layout = WidgetFactory.create_form_box(
            "",
            self.settings_layout,
            False,
            object_name="Error-Outer",
            title_color="#fcfcfc",
            title_font_size=18,
        )
        # self.settings_layout.addWidget(self.table_view_w)
        outter_layout.setContentsMargins(0, 0, 0, 0)
        outter_layout.setVerticalSpacing(15)

        top_button_layout = QHBoxLayout()

        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("title")
        self.clear_btn = GradientButton(
            "Clear All",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.clear_btn.setMaximumWidth(150)
        self.clear_btn.setFixedHeight(30)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.remove_succeeded_btn = GradientButton(
            "Remove Succeeded",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.remove_succeeded_btn.setMaximumWidth(150)
        self.remove_succeeded_btn.setFixedHeight(30)
        self.remove_succeeded_btn.setCursor(Qt.PointingHandCursor)
        top_button_layout.addWidget(self.title_label)
        h_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_button_layout.addItem(h_spacer)
        top_button_layout.addWidget(self.clear_btn)
        top_button_layout.addWidget(self.remove_succeeded_btn)
        top_button_layout.setContentsMargins(0, 0, 0, 0)

        outter_layout.addRow(top_button_layout)

        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
        )
        inner_layout.setContentsMargins(5, 5, 5, 10)
        inner_layout.setSpacing(5)
        inner_widget = QWidget()
        inner_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        inner_widget_layout = QFormLayout(inner_widget)
        inner_widget_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        summary_layout = QHBoxLayout()
        summary_layout.setAlignment(Qt.AlignHCenter)
        summary_layout.setContentsMargins(15, 15, 15, 15)
        summary_layout.setSpacing(50)
        # summary_layout.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.total_label = QLabel("Total: ")
        self.completed_label = QLabel("Completed: ")
        self.succeeded_label = QLabel("Succeeded:")
        self.failed_label = QLabel("Failed: ")
        self.retrying_label = QLabel("Retrying: ")
        self.stopped_label = QLabel("Stopped: ")
        self.pending_label = QLabel("Pending: ")

        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.completed_label)
        summary_layout.addWidget(self.succeeded_label)
        summary_layout.addWidget(self.failed_label)
        summary_layout.addWidget(self.retrying_label)
        summary_layout.addWidget(self.pending_label)

        outter_layout.addRow(summary_layout)
        # TABLE
        inner_layout.addRow(self.table_view_w)
        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.setObjectName("cancel-btn")
        self.cancel_btn.setMinimumWidth(250)
        self.cancel_btn.setFixedHeight(30)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)
        # btn_box.addItem(btn_spacer_1)
        btn_box.addWidget(self.cancel_btn, alignment=Qt.AlignHCenter)
        # btn_box.addItem(btn_spacer_2)
        outter_layout.addRow(btn_box)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)

        self.cancel_btn.clicked.connect(self.handle_cancel_clicked)
        self.clear_btn.clicked.connect(
            lambda: self.monitor_action.emit(MONITOREVENT.MONITOR_CLEAR_ALL)
        )

        self.remove_succeeded_btn.clicked.connect(
            lambda: self.monitor_action.emit(MONITOREVENT.MONITOR_REMOVE_SUCCEED)
        )

    def update_from_snapshot(self, snapshot: MonitorSnapShotEvent[RuleRunRow]) -> None:
        self.monitor_table_model.clear_model()
        self.monitor_table_model.update_data(snapshot.rows)
        self.handle_summary_update(snapshot.summary)

    def handle_cancel_clicked(self):
        self.reject()

    def handle_upsert_row(self, row: RuleRunRow):
        self.monitor_table_model.upsert_row(row)
        self.table_view_w.resizeColumnsToContents()

    def handle_summary_update(self, summary: RunSummary):
        self.total_label.setText(f"Total: {summary.total}")
        self.completed_label.setText(f"Completed: {summary.completed} ")
        self.succeeded_label.setText(f"Succeeded: {summary.succeeded}")
        self.failed_label.setText(f"Failed: {summary.failed}")
        self.retrying_label.setText(f"Retrying: {summary.retrying}")
        self.stopped_label.setText(f"Stopped: {summary.stopped}")
        self.pending_label.setText(f"Pending: {summary.pending}")
