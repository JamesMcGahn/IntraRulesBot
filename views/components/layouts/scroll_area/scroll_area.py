from PySide6.QtWidgets import QScrollArea

from .scroll_area_css import STYLES


class ScrollArea(QScrollArea):

    def __init__(self, parent):
        super().__init__(parent)

        self.setWidgetResizable(True)

        self.setStyleSheet(STYLES)
        self.corner_radius = 3
