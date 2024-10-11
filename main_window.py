from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow

from components.helpers import StyleHelper

# trunk-ignore(ruff/F401)
from resources import resources_rc
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
        self.resize(873, 800)
        self.setMaximumSize(QSize(873, 800))
        self.setMinimumSize(QSize(873, 800))

        font_id_reg = QFontDatabase.addApplicationFont(":/fonts/OpenSans-Regular.ttf")
        QFontDatabase.addApplicationFont(":/fonts/OpenSans-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id_reg)

        if font_family != -1:
            StyleHelper.dpi_scale_set_font(self.app, font_family, 13)

        self.centralWidget = CentralWidget()

        app_icon = QIcon()
        app_icon.addFile(":/icons/16_16.png", QSize(16, 16))
        app_icon.addFile(":/icons/24_24.png", QSize(24, 24))
        app_icon.addFile(":/icons/32_32.png", QSize(32, 32))
        app_icon.addFile(":/icons/48_48.png", QSize(48, 48))
        app_icon.addFile(":/icons/256_256.png", QSize(256, 256))
        app.setWindowIcon(app_icon)

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
