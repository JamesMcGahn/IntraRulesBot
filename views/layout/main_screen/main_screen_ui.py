from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy, QStackedWidget, QVBoxLayout, QWidget

from views.pages import LoginPage, LogsPage, RulesPage, SettingsPage


class MainScreenView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("main_screen_ui")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))

        self.main_screen_container_v = QVBoxLayout(self)
        self.main_screen_container_v.setObjectName("main_screen_container_v")
        self.main_screen_container_v.setContentsMargins(1, 1, 1, 1)
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("main_screen_stacked")

        self.rules_page = RulesPage()
        self.login_page = LoginPage()
        self.settings_page = SettingsPage()
        self.logs_page = LogsPage()

        self.stackedWidget.addWidget(self.login_page)
        self.stackedWidget.addWidget(self.rules_page)
        self.stackedWidget.addWidget(self.logs_page)
        self.stackedWidget.addWidget(self.settings_page)

        self.main_screen_container_v.addWidget(self.stackedWidget)
        self.stackedWidget.setCurrentIndex(1)
