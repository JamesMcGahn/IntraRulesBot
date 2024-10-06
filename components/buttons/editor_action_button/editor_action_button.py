import os
from typing import List, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QSizePolicy


class EditorActionButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text=text)

    # def enterEvent(self, event):
    #     self.setChecked(True)
    #     super().enterEvent(event)

    # def leaveEvent(self, event):
    #     self.setChecked(False)
    #     super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle the mouse press event."""
        if event.button() == Qt.LeftButton:
            self.setChecked(True)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.setChecked(False)
