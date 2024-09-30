import os
from typing import List, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGroupBox, QSizePolicy


class GradientGroupBox(QGroupBox):
    def __init__(
        self,
        title: str,
        title_color: str,
        gradient_colors: List[Tuple[float, str]],
        border_color: str = None,
        drop_shadow_effect: Union[
            Tuple[float, float, float, Union[str, QColor]], str
        ] = "default",
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
        self.border_width = 3
        self.corner_radius = 3
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "gradient_group_box.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Create and configure the drop shadow effect

        if self.drop_shadow_effect:
            if isinstance(self.drop_shadow_effect, str):
                if self.drop_shadow_effect == "default":
                    self.drop_shadow_effect = (8, 3, 3, QColor(0, 0, 0, 60))
                else:
                    raise ValueError("Invalid drop shadow effect preset.")
            radius, xoffset, yoffset, color = self.drop_shadow_effect
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setBlurRadius(radius)
            shadow_effect.setXOffset(xoffset)
            shadow_effect.setYOffset(yoffset)
            shadow_effect.setColor(color)

            self.setGraphicsEffect(shadow_effect)

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(self.xStart, self.yStart, self.xStop, self.yStop)
        for position, color in self.gradient_colors:
            gradient.setColorAt(position, color)

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.corner_radius, self.corner_radius)

        if self.border_color:

            painter.setPen(self.border_color)
            pen = QPen(self.border_color)
            pen.setWidth(self.border_width)
            painter.setPen(pen)

            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                self.rect().adjusted(
                    self.border_width - 2,
                    self.border_width - 2,
                    -self.border_width + 2,
                    -self.border_width + 2,
                ),
                3,
                3,
            )

        self.drawTitle(painter)

    def drawTitle(self, painter):
        # Set the title text color
        painter.setPen(self.title_color)
        painter.drawText(10, 15, self.title())

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()
