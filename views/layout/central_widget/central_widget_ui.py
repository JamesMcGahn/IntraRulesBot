from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget

from ..navbars import HeaderNavBar, IconOnlyNavBar, IconTextNavBar
from PySide6.QtGui import QLinearGradient, QPainter, QPaintEvent


class CentralWidgetView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.gridLayout)

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

    def add_widget_to_grid(
        self, widget: QWidget, row: int, col: int, rowSpan: int, intSpan: int
    ):
        self.gridLayout.addWidget(widget, row, col, rowSpan, intSpan)
