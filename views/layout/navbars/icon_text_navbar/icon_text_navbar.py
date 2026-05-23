from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import UIController

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .icon_text_navbar_css import STYLES
from .icon_text_navbar_ui import IconTextNavBarView


class IconTextNavBar(QWidget):
    """
    Controller class for the expanded side navigation bar with icons and text buttons.
    """

    btn_checked_ict = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self, ui_controller: UIController):
        super().__init__()
        self.setObjectName("icon_text_widget")
        self.setMaximumSize(QSize(250, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STYLES)
        self.ui_controller = ui_controller

        self.ui = IconTextNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        self.ui.page_change_request.connect(self.ui_controller.set_active_page)
        self.ui_controller.page_changed.connect(self.ui.sync_page)
        self.ui_controller.side_bar_changed.connect(self.hide_nav)
        self.setHidden(True)

    @Slot(bool)
    def hide_nav(self, checked: bool) -> None:
        """
        Slot to hide or show the navigation bar based on the checked state.
        """
        self.setHidden(not checked)
