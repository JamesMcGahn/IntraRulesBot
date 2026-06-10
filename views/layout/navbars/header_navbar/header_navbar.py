from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import TopNavControllers

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFileDialog

from base import QWidgetBase

from .header_navbar_css import STYLES
from .header_navbar_ui import HeaderNavBarView


class HeaderNavBar(QWidgetBase):
    """
    HeaderNavBar is the controller for the header navigation bar, managing user interactions such as
    toggling the hamburger menu and loading JSON files to validate rules.
    """

    hamburger_signal = Signal(bool)
    load_rules = Signal(list)

    def __init__(self, controllers: TopNavControllers):
        super().__init__()
        self.setObjectName("header_widget")
        self.setMaximumSize(QSize(16777215, 175))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)
        # View setup
        self.ui = HeaderNavBarView()
        self.layout.addWidget(self.ui)

        self.controllers = controllers
        self.rule_controller = self.controllers.rules
        self.ui_controller = self.controllers.ui
        # Connect signals
        self.ui.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)
        self.ui.open_file_btn.clicked.connect(self.open_json_file)

    def hamburger_icon_btn_toggled(self) -> None:
        """
        Slot for handling hamburger button toggle events. Emits the hamburger_signal.
        """
        self.ui_controller.set_side_bar(self.ui.hamburger_icon_btn.isChecked())

    def open_json_file(self) -> None:
        """
        Opens a file dialog to select a JSON file, passes filename to rules controller
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_name:
            self.rule_controller.import_from_file(file_name)
