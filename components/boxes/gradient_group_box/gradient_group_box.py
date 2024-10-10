from typing import List, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QGroupBox, QSizePolicy

from ...helpers import StyleHelper
from .gradient_group_box_styles import styles


class GradientGroupBox(QGroupBox):
    def __init__(
        self,
        title: str,
        title_color: str,
        gradient_colors: List[Tuple[float, str]],
        border_color: str = None,
        border_width: int = 2,
        corner_radius: int = 3,
        drop_shadow_effect: Union[
            Tuple[float, float, float, Union[str, QColor]], bool
        ] = True,
    ):
        super().__init__(title)
        self.gradient_colors = gradient_colors
        self.xStart = 0
        self.yStart = 0
        self.xStop = self.width()
        self.yStop = self.height()
        self.title_color = title_color
        self.border_color = border_color
        self.drop_shadow_effect = drop_shadow_effect
        self.border_width = border_width
        self.corner_radius = corner_radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet(styles)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Create and configure the drop shadow effect

        if self.drop_shadow_effect:
            if isinstance(self.drop_shadow_effect, bool):
                self.drop_shadow_effect = (8, 3, 3, QColor(0, 0, 0, 60))

            radius, xoffset, yoffset, color = self.drop_shadow_effect
            StyleHelper.drop_shadow(self, radius, xoffset, yoffset, color)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(self.xStart, self.yStart, self.xStop, self.yStop)
        for position, color in self.gradient_colors:
            gradient.setColorAt(position, color)
        painter.setBrush(Qt.NoBrush)
        painter.setBrush(gradient)
        # painter.setPen(Qt.NoPen)

        if self.border_color:

            painter.drawRoundedRect(
                self.contentsRect().adjusted(
                    self.border_width,
                    self.border_width,
                    -self.border_width,
                    -self.border_width,
                ),
                self.corner_radius,
                self.corner_radius,
            )

            painter.setPen(self.border_color)
            pen = QPen(self.border_color)
            pen.setWidth(self.border_width)
            painter.setPen(pen)

            painter.drawRoundedRect(
                self.contentsRect().adjusted(
                    self.border_width // 2,
                    self.border_width // 2,
                    -self.border_width // 2,
                    -self.border_width // 2,
                ),
                self.corner_radius,
                self.corner_radius,
            )
        else:
            painter.drawRoundedRect(self.rect(), self.corner_radius, self.corner_radius)

        self.drawTitle(painter)

    def drawTitle(self, painter):
        # Set the title text color
        painter.setPen(self.title_color)
        painter.drawText(10, 20, self.title())

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()
