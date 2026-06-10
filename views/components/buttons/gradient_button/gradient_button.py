from typing import List, Optional, Tuple, Union

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import (
    QColor,
    QFontMetrics,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QPushButton, QSizePolicy

from ...helpers import StyleHelper
from .gradient_button_css import STYLES


class GradientButton(QPushButton):
    """
    A QPushButton subclass that renders a button with a gradient background, border, and optional drop shadow.
    It can also handle icons and text rendering in various configurations.

    Args:
        text (str): The button label text.
        text_color (Union[str, QColor, None]): Color of the text.
        gradient_colors (List[Union[Tuple[float, str], Tuple[float, QColor]]]): List of gradient stops and colors.
        border_color (Union[str, QColor, None], optional): Color of the button border. Defaults to None.
        border_width (int, optional): Width of the button border. Defaults to 3.
        corner_radius (int, optional): Radius of the button corners. Defaults to 3.
        drop_shadow_effect (Union[Tuple[float, float, float, Union[str, QColor]], bool], optional):
            Drop shadow effect as a tuple (radius, xoffset, yoffset, color) or a boolean. Defaults to True.
    """

    def __init__(
        self,
        text: str,
        text_color: Union[str, QColor, None],
        gradient_colors: List[Union[Tuple[float, str], Tuple[float, QColor]]],
        border_color: Optional[Union[str, QColor]] = None,
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
        self.toggled.connect(self.on_toggled)
        # Create and configure the drop shadow effect

        if self.drop_shadow_effect:
            if isinstance(self.drop_shadow_effect, bool):
                self.drop_shadow_effect = (8, 3, 3, QColor(0, 0, 0, 60))

            radius, xoffset, yoffset, color = self.drop_shadow_effect
            StyleHelper.drop_shadow(self, radius, xoffset, yoffset, color)

    def paintEvent(self, event: QPainter) -> None:
        """
        Override paintEvent to custom paint the button with gradient and border.

        Args:
            event: The paint event triggered by Qt.

        Returns:
            None: This function does not return a value.
        """

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

    def drawTitle(self, painter: QPainter) -> None:
        """
        Draw the text and icon (if present) in the button.

        Args:
            painter (QPainter): The QPainter object used to draw.

        Returns:
            None: This function does not return a value.
        """
        if not self.text_color:
            self.text_color = "black"
        painter.setPen(QColor(self.text_color))

        text_rect = self.contentsRect()

        icon_size = self.iconSize()
        if not self.icon().isNull():
            font_metrics = QFontMetrics(self.font())
            text_height = font_metrics.boundingRect(self.text()).height()
            text_width = font_metrics.boundingRect(self.text()).width()
            icon = self.icon()

            width = (
                (icon_size.width() + text_width) // 2
                if self.text()
                else (icon_size.width() // 2)
            )
            icon_rect = QRect(
                self.contentsRect().center().x() - width,
                (self.height() - icon_size.height()) // 2,
                icon_size.width(),
                icon_size.height(),
            )

            icon.paint(painter, icon_rect, Qt.AlignCenter)

            text_height = font_metrics.boundingRect(self.text()).height()
            text_width = font_metrics.boundingRect(self.text()).width()

            text_rect = QRect(
                icon_rect.right(),
                (self.height() - text_height) // 2,
                text_width,
                text_height,
            )
            # Adjust text position to accommodate the icon
            text_rect.setLeft(icon_rect.right())
            painter.drawText(text_rect, Qt.AlignLeft, self.text())
        else:
            painter.drawText(text_rect, Qt.AlignCenter, self.text())

    def on_toggled(self, checked: bool) -> None:
        """
        Slot triggered when the button's checked state changes.

        Args:
            checked (bool): True if the button is checked, False otherwise.

        Returns:
            None: This function does not return a value.
        """
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle the mouse press event and set the button's pressed state.

        Args:
            event: The mouse press event.

        Returns:
            None: This function does not return a value.
        """

        if event.button() == Qt.LeftButton:
            self.pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle the mouse release event and reset the button's pressed state.

        Args:
            event: The mouse release event.

        Returns:
            None: This function does not return a value.
        """
        if event.button() == Qt.LeftButton:
            self.pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        """
        Set the gradient start and stop positions.

        Args:
            xStart (float): The X coordinate for the gradient start.
            yStart (float): The Y coordinate for the gradient start.
            xStop (float): The X coordinate for the gradient stop.
            yStop (float): The Y coordinate for the gradient stop.

        Returns:
            None: This function does not return a value.
        """
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()
