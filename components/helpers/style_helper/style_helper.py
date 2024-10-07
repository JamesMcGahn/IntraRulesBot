from typing import Union

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class StyleHelper:

    @staticmethod
    def drop_shadow(
        parent,
        blur_radius=5,
        x_offset=3,
        y_offset=3,
        color: Union[str, QColor] = None,
    ):
        if color is None:
            color = QColor(0, 0, 0, 60)

        shadow_effect = QGraphicsDropShadowEffect(parent)
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setXOffset(x_offset)
        shadow_effect.setYOffset(y_offset)
        shadow_effect.setColor(QColor(color))
        parent.setGraphicsEffect(shadow_effect)
