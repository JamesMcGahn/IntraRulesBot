from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import CentralWidgetControllers

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QLinearGradient, QPainter, QPaintEvent

from base import QWidgetBase

from ..main_screen import MainScreen
from ..navbars import HeaderNavBar, IconOnlyNavBar, IconTextNavBar
from .central_widget_ui import CentralWidgetView


class CentralWidget(QWidgetBase):
    close_main_window = Signal()

    def __init__(self, controllers: CentralWidgetControllers):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.ui = CentralWidgetView()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)
        # main_layout = QVBoxLayout(self)

        self.ui_controller = controllers.ui
        self.ui_controller.set_parent_widget(self)

        self.icon_only_widget = IconOnlyNavBar(ui_controller=self.ui_controller)
        self.icon_text_widget = IconTextNavBar(ui_controller=self.ui_controller)

        self.header_widget = HeaderNavBar(controllers=controllers.top_nav)
        self.main_screen_widget = MainScreen(controllers=controllers.main_screen)
        self.ui.add_widget_to_grid(self.main_screen_widget, 2, 3, 1, 1)
        self.ui.add_widget_to_grid(self.icon_only_widget, 0, 1, 3, 1)
        self.ui.add_widget_to_grid(self.icon_text_widget, 0, 2, 3, 1)
        self.ui.add_widget_to_grid(self.header_widget, 0, 3, 1, 1)

        self.main_screen_widget.send_logs.connect(self.logging)
        self.prepare_ui_for_shutdown.connect(
            self.main_screen_widget.notified_app_shutting
        )

        self.header_widget.hamburger_signal.connect(self.icon_only_widget.hide_nav)
        self.header_widget.hamburger_signal.connect(self.icon_text_widget.hide_nav)

        self.main_screen_widget.close_main_window.connect(self.close_icon_clicked)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Custom paint event to draw a linear gradient background on the central widget.
        """
        painter = QPainter(self)
        gradient = QLinearGradient(self.width() / 2, 0, self.width() / 2, self.height())
        gradient.setColorAt(0.05, "#228752")  #
        gradient.setColorAt(0.75, "#014637")
        gradient.setColorAt(1, "#014637")
        painter.setBrush(gradient)
        painter.drawRect(self.rect())

    @Slot()
    def close_icon_clicked(self) -> None:
        """
        Slot emits signal close_main_window to close main window
        """
        self.close_main_window.emit()
