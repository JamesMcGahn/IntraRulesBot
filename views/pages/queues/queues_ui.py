from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QProgressBar,
)


from views.components.buttons import GradientButton
from views.components.helpers import WidgetFactory

from .enums.queues_page_event import QUEUESPAGEEVENT
from .models.queues_page_action import QueuesPageAction
from controllers.queues.models.spread_sheet_import import SpreadSheetImport
from services.queue_runner.enums.queue_runner_lifecyle import QUEUERUNNERLIFECYCLE


class QueuesPageView(QWidget):
    """
    View class for the login page, providing UI components for user credential input.
    """

    queues_page_action = Signal(object)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Sets up the UI layout and components for the login page.
        """
        self.queues_layout = QVBoxLayout(self)
        # Outer layout for the form

        outter_layout = WidgetFactory.create_form_box(
            "Queues Information",
            self.queues_layout,
            False,
            object_name="Login-Information",
            title_color="#fcfcfc",
        )
        # Inner layout to center the input fields
        inner_h_layout = QHBoxLayout()
        # Inner layout for the actual form inputs
        inner_layout = WidgetFactory.create_form_box(
            "",
            inner_h_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            max_width=400,
        )

        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outter_layout.addRow(inner_h_layout)
        self.settings_grid_layout = QGridLayout()
        inner_layout.addRow(self.settings_grid_layout)

        file_loc_label = QLabel("File Location")
        file_loc_label.setStyleSheet("color:black; margin-top: 3px;")
        self.settings_grid_layout.addWidget(file_loc_label, 0, 0, Qt.AlignTop)

        file_location_layout = QHBoxLayout()
        file_location_layout.setAlignment(Qt.AlignLeft)

        folder_icon_button = GradientButton(
            "  Open File",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )

        folder_icon_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        folder_icon_button.setStyleSheet("padding: 3px;")
        folder_icon_button.setFixedHeight(18)
        folder_icon_button.setCursor(Qt.PointingHandCursor)

        WidgetFactory.create_icon(
            folder_icon_button,
            ":/images/open_folder_on.png",
            15,
            15,
            True,
            False,
        )

        folder_icon_button.clicked.connect(self.open_folder_dialog)
        # folder_icon_button.clicked.connect(
        #     lambda: self.open_folder_dialog(tab, key, widget_type)
        # )
        self.file_loc_line_edit_field = QLineEdit()
        self.file_loc_line_edit_field.setStyleSheet("background-color: #FCFCFC;")
        self.file_loc_line_edit_field.setText(str(""))
        self.file_loc_line_edit_field.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )

        file_location_layout.addWidget(self.file_loc_line_edit_field)
        file_location_layout.addWidget(folder_icon_button)
        self.settings_grid_layout.addLayout(file_location_layout, 0, 1, Qt.AlignBottom)

        prod_name_label = QLabel("Provider Name:")
        prod_name_label.setStyleSheet("color:black; margin-top: 3px;")
        self.settings_grid_layout.addWidget(prod_name_label, 1, 0, Qt.AlignTop)

        self.prod_name_line_edit_field = QLineEdit()
        self.prod_name_line_edit_field.setStyleSheet("background-color: #FCFCFC;")
        self.prod_name_line_edit_field.setText(str(""))
        self.prod_name_line_edit_field.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.settings_grid_layout.addWidget(
            self.prod_name_line_edit_field, 1, 1, Qt.AlignTop
        )

        prod_inst_label = QLabel("Provider Instance:")
        prod_inst_label.setStyleSheet("color:black; margin-top: 3px;")
        self.settings_grid_layout.addWidget(prod_inst_label, 2, 0, Qt.AlignTop)

        self.prod_inst_line_edit_field = QLineEdit()
        self.prod_inst_line_edit_field.setStyleSheet("background-color: #FCFCFC;")
        self.prod_inst_line_edit_field.setText(str(""))
        self.prod_inst_line_edit_field.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.settings_grid_layout.addWidget(
            self.prod_inst_line_edit_field, 2, 1, Qt.AlignTop
        )

        self.run_button = GradientButton(
            "",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )

        self.monitor_button = GradientButton(
            "",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.stop_button = GradientButton(
            "",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )

        WidgetFactory.create_icon(
            self.run_button,
            ":/images/play.png",
            15,
            15,
            True,
            False,
        )

        WidgetFactory.create_icon(
            self.monitor_button,
            ":/images/monitor.png",
            15,
            15,
            True,
            False,
        )
        WidgetFactory.create_icon(
            self.stop_button,
            ":/images/stop.png",
            15,
            15,
            True,
            False,
        )

        self.run_button.setProperty("page_action", QUEUESPAGEEVENT.START_RUNNER)
        self.monitor_button.setProperty(
            "page_action", QUEUESPAGEEVENT.TOGGLE_DISPLAY_MONITOR
        )
        self.stop_button.setProperty("page_action", QUEUESPAGEEVENT.STOP_RUNNER)
        self.stop_button.setHidden(True)
        self.monitor_button.setProperty(
            "page_action", QUEUESPAGEEVENT.TOGGLE_DISPLAY_MONITOR
        )
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(self.monitor_button)
        thread_layout.addWidget(self.run_button)
        thread_layout.addWidget(self.stop_button)

        self.settings_grid_layout.addLayout(thread_layout, 3, 1)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setHidden(True)
        self.settings_grid_layout.addWidget(self.progress_bar, 4, 1)
        self.run_button.clicked.connect(self.handle_action_button_click)
        self.stop_button.clicked.connect(self.handle_action_button_click)
        self.monitor_button.clicked.connect(self.handle_action_button_click)

    def handle_action_button_click(self):
        sender = self.sender()
        if sender is None:
            return

        raw_action = sender.property("page_action")
        if raw_action is None:
            return

        action = QUEUESPAGEEVENT(raw_action)
        payload = self._build_action_payload(action)
        if payload is None:
            return
        self.queues_page_action.emit(payload)

    def _build_action_payload(self, action: QUEUESPAGEEVENT):
        if action == QUEUESPAGEEVENT.START_RUNNER:
            return QueuesPageAction[dict[str, str]](action, self._get_form_inputs())
        elif action == QUEUESPAGEEVENT.STOP_RUNNER:
            return QueuesPageAction(action, None)
        elif action == QUEUESPAGEEVENT.TOGGLE_DISPLAY_MONITOR:
            return QueuesPageAction(action, None)

    def _get_form_inputs(self) -> dict[str, str]:
        return SpreadSheetImport(
            file_location=self.file_loc_line_edit_field.text(),
            provider_name=self.prod_name_line_edit_field.text(),
            provider_instance=self.prod_inst_line_edit_field.text(),
        )

    def open_folder_dialog(self) -> None:
        """
        Opens a dialog for the user to select a folder for storing log files.
        Once a folder is selected, the path is updated in the corresponding input field.

        Returns:
            None: This function does not return a value.
        """

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Queues Excel File",
            "./",
            "Excel Files (*.xlsx *.xls)",
        )

        self.file_loc_line_edit_field.blockSignals(True)
        self.file_loc_line_edit_field.setText(file_name)
        self.file_loc_line_edit_field.blockSignals(False)

    @Slot(object)
    def handle_queue_runner_state_update(self, state: QUEUERUNNERLIFECYCLE) -> None:
        if state == QUEUERUNNERLIFECYCLE.STARTED:
            self.stop_button.setHidden(False)
            self.progress_bar.setHidden(False)
            self.progress_bar.setValue(0)
            self.run_button.setDisabled(True)
        if state == QUEUERUNNERLIFECYCLE.FINISHED:
            self.stop_button.setHidden(True)
            self.run_button.setDisabled(False)
            QTimer.singleShot(5000, lambda: self.progress_bar.setHidden(True))

    @Slot(int, int)
    def set_progress_bar(self, current: int, total: int) -> None:
        """
        Updates the rules progress bar.
        """
        self.progress_bar.setHidden(False)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
