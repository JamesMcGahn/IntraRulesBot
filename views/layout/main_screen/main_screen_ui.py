from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ...base.enums import PAGE
from ...components.layouts import StackedWidget


class MainScreenView(QWidget):
    """
    MainScreenView is the view component for the main screen. It manages the UI layout
    and holds different pages like login, rules, settings, and logs using QStackedWidget.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """init MainScreen View"""
        self.setObjectName("main_screen_ui")
        # Set size policy
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))

        # Main layout container
        self.main_screen_container_v = QVBoxLayout(self)
        self.main_screen_container_v.setObjectName("main_screen_container_v")
        self.main_screen_container_v.setContentsMargins(1, 1, 1, 1)
        # Stacked widget to hold multiple pages
        self.stackedWidget = StackedWidget(self)
        self.stackedWidget.setObjectName("main_screen_stacked")

        # Add the stacked widget to the main layout
        self.main_screen_container_v.addWidget(self.stackedWidget)

    def add_page_to_stacked_widget(self, page_name: PAGE, widget: QWidget):
        self.stackedWidget.add_widget(page_name, widget)

    def switch_page(self, page_name: PAGE):
        self.stackedWidget.set_current_by_name(page_name)
