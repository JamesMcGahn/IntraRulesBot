from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QLabel, QMainWindow

import resources_rc as resources_rc
from services.logger import Logger
from views.layout import CentralWidget


class MainWindow(QMainWindow):
    appshutdown = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowTitle("IntraRulesBot")
        self.setObjectName("MainWindow")
        self.resize(900, 800)
        self.setMaximumSize(QSize(16777215, 16777215))

        font_id_reg = QFontDatabase.addApplicationFont(":/fonts/OpenSans-Regular.ttf")
        QFontDatabase.addApplicationFont(":/fonts/OpenSans-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id_reg)

        if font_family != -1:
            self.app.setFont(font_family)

        self.centralWidget = CentralWidget()

        self.label = QLabel(self)
        self.setCentralWidget(self.centralWidget)
        self.logger = Logger(turn_off_print=False)
        self.send_logs.connect(self.logger.insert)
        self.centralWidget.send_logs.connect(self.logger.insert)
        self.appshutdown.connect(self.logger.close)
        self.appshutdown.connect(self.centralWidget.notified_app_shutting)

    # TODO - close event - shut down threads
    def closeEvent(self, event):
        self.send_logs.emit("Closing Application", "INFO", True)
        self.appshutdown.emit()
        event.accept()
