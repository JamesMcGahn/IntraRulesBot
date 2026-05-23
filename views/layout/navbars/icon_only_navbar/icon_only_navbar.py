from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import UIController

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from views.components.helpers import StyleHelper

from .icon_only_navbar_css import STYLES
from .icon_only_navbar_ui import IconOnlyNavBarView


class IconOnlyNavBar(QWidget):
    """
    Controller for the compressed side navigation bar with icon-only buttons.
    This class manages the behavior of the navigation buttons, including toggling
    and page changes.
    """

    btn_checked_ico = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self, ui_controller: UIController):
        """
        Initializes the IconOnlyNavBar controller, connects signals to handle button interactions,
        and sets default states for the buttons.
        """
        super().__init__()
        self.setObjectName("icon_only_widget")
        self.setMaximumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STYLES)
        self.ui_controller = ui_controller
        # Set up the UI
        self.ui = IconOnlyNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        StyleHelper.drop_shadow(self)

        self.ui.page_change_request.connect(self.ui_controller.set_active_page)
        self.ui_controller.page_changed.connect(self.ui.sync_page)
        self.ui_controller.side_bar_changed.connect(self.hide_nav)

    @Slot(bool)
    def hide_nav(self, checked: bool) -> None:
        """
        Slot to hide or show the navigation bar based on the checked state.
        """
        self.setHidden(checked)
