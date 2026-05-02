from typing import List, Optional, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QGroupBox, QSizePolicy

from ...helpers import StyleHelper
from .gradient_group_box_styles import styles


class GradientGroupBox(QGroupBox):
    """
    A custom QGroupBox widget that displays a gradient background, with optional border and drop shadow effects.

    This class allows you to customize the title color, background gradient, border color, and drop shadow.

    Args:
        title (str): The title of the group box.
        title_color (str): The color of the title text.
        gradient_colors (List[Tuple[float, str]]): A list of tuples representing the position and color of the gradient.
        border_color (Optional[str], optional): The color of the border. Defaults to None.
        border_width (int, optional): The width of the border in pixels. Defaults to 2.
        corner_radius (int, optional): The radius of the corners in pixels. Defaults to 3.
        drop_shadow_effect (Union[Tuple[float, float, float, Union[str, QColor]], bool], optional): A tuple representing
        drop shadow properties (radius, x offset, y offset, color) or a boolean to enable a default shadow. Defaults to True.
    """

    def __init__(
        self,
        title: str,
        title_color: str,
        gradient_colors: List[Tuple[float, str]],
        border_color: Optional[str] = None,
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

    def paintEvent(self, event: QPainter) -> None:
        """
        Paints the widget using a gradient background and optional border.

        This method is responsible for rendering the gradient and the border on the widget.

        Returns:
            None: This function does not return a value.
        """

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

    def drawTitle(self, painter: QPainter):
        """
        Draws the title text in the specified title color.

        Args:
            painter (QPainter): The QPainter object used for rendering.

        Returns:
            None: This function does not return a value.
        """
        painter.setPen(self.title_color)
        painter.drawText(10, 20, self.title())

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        """
        Set the start and stop points for the gradient.

        Args:
            xStart (float): The x-coordinate for the start of the gradient.
            yStart (float): The y-coordinate for the start of the gradient.
            xStop (float): The x-coordinate for the end of the gradient.
            yStop (float): The y-coordinate for the end of the gradient.

        Returns:
            None: This function does not return a value.
        """
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()
