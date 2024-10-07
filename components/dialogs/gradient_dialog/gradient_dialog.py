from typing import List, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QDialog


class GradientDialog(QDialog):
    def __init__(
        self, gradient_colors: List[Tuple[float, Union[QColor, str]]], parent=None
    ):
        super().__init__(parent)
        self.gradient_colors = gradient_colors
        self.xStart = 0
        self.yStart = 0
        self.xStop = self.width()
        self.yStop = self.height()

        self.setMinimumHeight(300)
        self.setMinimumWidth(300)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(self.xStart, self.yStart, self.xStop, self.yStop)
        for position, color in self.gradient_colors:
            gradient.setColorAt(position, color)
        painter.setBrush(Qt.NoBrush)
        painter.fillRect(self.rect(), gradient)

    def resizeEvent(self, event):
        width_ratio = self.width() / self.xStop if self.xStop != 0 else 1
        height_ratio = self.height() / self.yStop if self.yStop != 0 else 1

        new_xStart = self.xStart * width_ratio
        new_yStart = self.yStart * height_ratio
        new_xStop = self.xStop * width_ratio
        new_yStop = self.yStop * height_ratio

        self.set_gradient_start_stop(new_xStart, new_yStart, new_xStop, new_yStop)

        super().resizeEvent(event)

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()
