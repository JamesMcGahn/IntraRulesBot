import os

from PySide6.QtWidgets import QScrollArea


class ScrollArea(QScrollArea):

    def __init__(self, parent):
        super().__init__(parent)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "scroll_area.css")
        self.setWidgetResizable(True)
        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())
        self.corner_radius = 3
