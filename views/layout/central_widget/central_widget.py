from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QLinearGradient, QPainter, QPaintEvent
from PySide6.QtWidgets import QGridLayout

from base import QWidgetBase

from ..main_screen import MainScreen
from ..navbars import HeaderNavBar, IconOnlyNavBar, IconTextNavBar


class CentralWidget(QWidgetBase):
    close_main_window = Signal()

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)

        # main_layout = QVBoxLayout(self)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.icon_only_widget = IconOnlyNavBar()
        self.icon_text_widget = IconTextNavBar()

        self.header_widget = HeaderNavBar()
        self.main_screen_widget = MainScreen()
        self.gridLayout.addWidget(self.main_screen_widget, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.icon_only_widget, 0, 1, 3, 1)
        self.gridLayout.addWidget(self.icon_text_widget, 0, 2, 3, 1)
        self.gridLayout.addWidget(self.header_widget, 0, 3, 1, 1)
        self.setLayout(self.gridLayout)

        self.main_screen_widget.send_logs.connect(self.logging)
        self.appshutdown.connect(self.main_screen_widget.notified_app_shutting)

        self.header_widget.hamburger_signal.connect(self.icon_only_widget.hide_nav)
        self.header_widget.hamburger_signal.connect(self.icon_text_widget.hide_nav)

        self.icon_only_widget.btn_checked_ico.connect(
            self.icon_text_widget.btns_set_checked
        )
        self.icon_text_widget.btn_checked_ict.connect(
            self.icon_only_widget.btns_set_checked
        )

        self.icon_only_widget.btn_clicked_page.connect(
            self.main_screen_widget.change_page
        )
        self.icon_text_widget.btn_clicked_page.connect(
            self.main_screen_widget.change_page
        )
        self.main_screen_widget.close_main_window.connect(self.close_icon_clicked)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Custom paint event to draw a linear gradient background on the central widget.

        Args:
            event (QPaintEvent): The paint event.

        Returns:
            None: This function does not return a value.

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

        Returns:
            None: This function does not return a value.
        """
        self.close_main_window.emit()
