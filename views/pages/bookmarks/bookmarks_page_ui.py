from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from components.helpers import WidgetFactory
from components.layouts import ScrollArea

from .bookmarks_page_css import SCROLL_AREA_STYLES


class BookMarksPageView(QWidget):
    """
    A UI component that represents the Bookmarks display page.

    Signals:


    Attributes:
    """

    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the UI components of the Bookmarks page, including the layout and
        the text display for bookmarks.

        Returns:
            None: This function does not return a value.
        """
        self.settings_layout = QVBoxLayout(self)

        outter_layout = WidgetFactory.create_form_box(
            "Rule Sets",
            self.settings_layout,
            False,
            object_name="Rule-Sets",
            title_color="#fcfcfc",
        )

        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
        )
