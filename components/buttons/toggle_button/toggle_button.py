from typing import Tuple, Union

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QCheckBox

from ...helpers import StyleHelper


class ToggleButton(QCheckBox):
    def __init__(
        self,
        width: int = 60,
        height: int = 28,
        background_color: Union[str, QColor] = "dark gray",
        active_background_color: Union[str, QColor] = "dark gray",
        circle_color: Union[str, QColor] = "light gray",
        drop_shadow_effect: Union[
            Tuple[float, float, float, Union[str, QColor]], bool
        ] = True,
    ):
        super().__init__()
        width = width
        height = height
        self.background_color = background_color
        self.circle_color = circle_color
        self.active_background_color = active_background_color
        self.drop_shadow_effect = drop_shadow_effect
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)

        if self.drop_shadow_effect:
            if isinstance(self.drop_shadow_effect, bool):
                self.drop_shadow_effect = (8, 3, 3, QColor(0, 0, 0, 60))

            radius, xoffset, yoffset, color = self.drop_shadow_effect
            StyleHelper.drop_shadow(self, radius, xoffset, yoffset, color)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        rect = QRect(0, 0, self.width(), self.height())

        if self.isChecked():
            painter.setBrush(QColor(self.active_background_color))
        else:
            painter.setBrush(QColor(self.background_color))

        painter.drawRoundedRect(
            0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2
        )

        painter.setBrush(QColor(self.circle_color))
        circle_x = self.width() - (self.height() / 2) * 2 if self.isChecked() else 0
        painter.drawEllipse(
            circle_x, 0, (self.height() / 2) * 2, (self.height() / 2) * 2
        )