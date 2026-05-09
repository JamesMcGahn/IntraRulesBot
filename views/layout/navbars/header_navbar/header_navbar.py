from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import ControllerFactory


from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QFileDialog

from base import QWidgetBase


from .header_navbar_css import STYLES
from .header_navbar_ui import HeaderNavBarView
from base.events import UIEvent, ToastEvent, SchemaErrorDialogEvent


class HeaderNavBar(QWidgetBase):
    """
    HeaderNavBar is the controller for the header navigation bar, managing user interactions such as
    toggling the hamburger menu and loading JSON files to validate rules.

    Signals:
        hamburger_signal (Signal[bool]): Emitted when the hamburger menu button is toggled.
        load_rules (Signal[list]): Emitted to load rules into the RulesModel.

    Attributes:
        ui (HeaderNavBarView): The view component that defines the layout and widgets.
        val (SchemaValidator): Validator used to validate the JSON file against the rules schema.
        total_errors (int): Total count of errors found during JSON validation.
        rules_errors (list): List of rule validation errors.
        json_decode_error (str): Error message when JSON decoding fails.
        file_failed (bool): Flag indicating if loading the file failed.
        rules (RulesModel): Model for managing rules.
    """

    hamburger_signal = Signal(bool)
    load_rules = Signal(list)

    def __init__(self, controller_factory: ControllerFactory):
        """
        Initializes the HeaderNavBar, sets up the view and connections, and prepares the rule validation.
        """
        super().__init__()
        self.setObjectName("header_widget")
        self.setMaximumSize(QSize(16777215, 175))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)
        # View setup
        self.ui = HeaderNavBarView()
        self.layout.addWidget(self.ui)

        self.controller_factory = controller_factory
        self.top_nav_controllers = self.controller_factory.create_top_nav_bar()
        self.rule_controller = self.top_nav_controllers.rules
        # Connect signals
        self.ui.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)
        self.ui.open_file_btn.clicked.connect(self.open_json_file)

    def hamburger_icon_btn_toggled(self) -> None:
        """
        Slot for handling hamburger button toggle events. Emits the hamburger_signal.

        Returns:
            None: This function does not return a value.
        """
        self.hamburger_signal.emit(self.ui.hamburger_icon_btn.isChecked())

    def open_json_file(self) -> None:
        """
        Opens a file dialog to select a JSON file, validates its content against the rules schema,
        and emits the valid data to the RulesModel. Displays errors if validation fails.

        Returns:
            None: This function does not return a value.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_name:
            self.rule_controller.import_from_file(file_name)
