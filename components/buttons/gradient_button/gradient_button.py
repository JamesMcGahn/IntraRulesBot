from typing import List, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QPushButton, QSizePolicy

from ...helpers import StyleHelper
from .gradient_button_css import STYLES


class GradientButton(QPushButton):
    def __init__(
        self,
        text: str,
        text_color: Union[str, QColor, None],
        gradient_colors: List[Union[Tuple[float, str], Tuple[float, QColor]]],
        border_color: Union[str, QColor, None] = None,
        border_width: int = 3,
        corner_radius: int = 3,
        drop_shadow_effect: Union[
            Tuple[float, float, float, Union[str, QColor]], bool
        ] = True,
    ):
        super().__init__(text=text)
        self.gradient_colors = gradient_colors
        self.xStart = self.contentsRect().width() / 2
        self.yStart = 0
        self.xStop = self.contentsRect().width() / 2
        self.yStop = self.contentsRect().height()
        self.text_color = text_color
        self.border_color = border_color
        self.drop_shadow_effect = drop_shadow_effect
        self.border_width = border_width
        self.corner_radius = corner_radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.is_hovered = False
        self.pressed = False
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(STYLES)

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
            gradient.setColorAt(position, QColor(color))
        painter.setBrush(Qt.NoBrush)
        painter.setBrush(gradient)

        gradient2 = QLinearGradient(
            self.contentsRect().width() / 2,
            0,
            self.contentsRect().width() / 2,
            self.contentsRect().height(),
        )
        if self.pressed:
            # gradient2.setColorAt(0.25, "light gray")

            for position, color in self.gradient_colors:
                color_a = QColor(color)
                if position >= 0.85:

                    color = QColor(color_a.red(), color_a.green(), color_a.blue(), 200)
                elif position >= 0.50:
                    color = QColor(color_a.red(), color_a.green(), color_a.blue(), 220)
                elif position >= 0.25:
                    color = QColor(color_a.red(), color_a.green(), color_a.blue(), 235)
                elif position >= 0:
                    color = QColor(color_a.red(), color_a.green(), color_a.blue(), 255)
                gradient2.setColorAt(position, color)

            painter.setBrush(gradient2)
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

            pen = QPen(QColor(self.border_color))
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
        if not self.text_color:
            self.text_color = "black"
        painter.setPen(QColor(self.text_color))
        text_rect = self.contentsRect()
        painter.drawText(text_rect, Qt.AlignCenter, self.text())

    # def enterEvent(self, event):
    #     self.is_hovered = True
    #     self.update()  # Update the button to repaint

    # def leaveEvent(self, event):
    #     self.is_hovered = False
    #     self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()
