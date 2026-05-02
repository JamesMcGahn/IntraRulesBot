from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from .enums import QTOASTSTATUS
from PySide6.QtGui import QColor, QFont

from .pyqttoast import Toast, ToastPosition


class QToast(Toast):

    def __init__(self, parent: QWidget, status: QTOASTSTATUS, title: str, message: str):
        super().__init__(parent)
        self.setDuration(5000)
        self.message = message
        self.title = title
        self.status = status

        font = QFont([".AppleSystemUIFont"], 12, QFont.Weight.Bold)
        self.setTitleFont(font)
        self.setTextFont(font)
        self.applyPreset(self.status)
        self.setTextColor(QColor("#ffffff"))
        self.setTitleColor(QColor("#FFFFFF"))
        self.setBackgroundColor(QColor("#014637"))
        self.setDurationBarColor(QColor("#f58220"))
        self.setIconSeparatorColor(QColor("#f58220"))
        self.setIconColor(QColor("#f58220"))
        self.setCloseButtonIconColor(QColor("#f58220"))
        self.setMinimumWidth(300)
        self.setMaximumWidth(350)
        self.setMinimumHeight(55)
        self.setBorderRadius(3)
        self.setPosition(ToastPosition.BOTTOM_RIGHT)
        self.setTitle(self.title)
        self.setText(self.message)
