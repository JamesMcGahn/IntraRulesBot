from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .main_screen_ui import MainScreenView


class MainScreen(QWidget):
    appshutdown = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self):
        super().__init__()
        self.ui = MainScreenView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.setObjectName("main_screen")

        self.ui.rules_page.send_logs.connect(self.logging)
        self.appshutdown.connect(self.ui.rules_page.notified_app_shutting)

    @Slot(QPushButton)
    def change_page(self, btn):
        btn_name = btn.objectName()

        if btn_name.startswith("keys_btn_"):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif btn_name.startswith("rules_btn_"):
            self.ui.stackedWidget.setCurrentIndex(1)
        elif btn_name.startswith("logs_btn_"):
            self.ui.stackedWidget.setCurrentIndex(2)
        elif btn_name.startswith("settings_btn_"):
            self.ui.stackedWidget.setCurrentIndex(3)

    @Slot(str, str, bool)
    def logging(self, msg, level="INFO", print_msg=True):
        self.send_logs.emit(msg, level, print_msg)

    @Slot()
    def notified_app_shutting(self):
        self.appshutdown.emit()
