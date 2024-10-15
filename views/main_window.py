from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFontDatabase, QIcon
from PySide6.QtWidgets import QMainWindow, QMenu, QSystemTrayIcon

from components.dialogs import ConfirmationDialog
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
        # Load and set fonts
        font_id_reg = QFontDatabase.addApplicationFont(":/fonts/OpenSans-Regular.ttf")
        QFontDatabase.addApplicationFont(":/fonts/OpenSans-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id_reg)

        if font_family != -1:
            StyleHelper.dpi_scale_set_font(self.app, font_family, 13)
        # Initialize central widget
        self.centralWidget = CentralWidget()
        # Set application icon
        app_icon = QIcon()
        app_icon.addFile(":/system_icons/logo16_16.ico", QSize(16, 16))
        app_icon.addFile(":/system_icons/logo24_24.ico", QSize(24, 24))
        app_icon.addFile(":/system_icons/logo32_32.ico", QSize(32, 32))
        app_icon.addFile(":/system_icons/logo48_48.ico", QSize(48, 48))
        app_icon.addFile(":/system_icons/logo256_256.ico", QSize(256, 256))
        self.app.setWindowIcon(app_icon)

        # Set system tray icon
        tray_icon = QSystemTrayIcon(app_icon, self.app)
        tray_menu = QMenu()
        maximize_action = QAction("Maximize", self)
        minimize_action = QAction("Minimize", self)
        quit_action = QAction("Quit", self)
        maximize_action.triggered.connect(self.showNormal)
        minimize_action.triggered.connect(self.showMinimized)
        quit_action.triggered.connect(self.close_main_window)
        tray_menu.addAction(maximize_action)
        tray_menu.addAction(minimize_action)
        tray_menu.addAction(quit_action)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()

        tray_icon.activated.connect(self.on_tray_icon_click)

        # Set the central widget and logger
        self.setCentralWidget(self.centralWidget)
        self.logger = Logger(turn_off_print=False)
        self.send_logs.connect(self.logger.insert)
        self.centralWidget.send_logs.connect(self.logger.insert)
        self.centralWidget.close_main_window.connect(self.close_main_window)
        self.appshutdown.connect(self.logger.close)
        self.appshutdown.connect(self.centralWidget.notified_app_shutting)

    def on_tray_icon_click(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon click events. If minimized, show window as normal and bring to the font.
        If the window is already displayed, minimize the window.
        Args:
            reason (QSystemTrayIcon.ActivationReason): ActivationReason event when user clicks on the tray icon
        Returns:
            None: This function does not return a value.
        """
        if reason == QSystemTrayIcon.Trigger:
            # If the window is minimized, show it
            if self.isMinimized():
                self.showNormal()
                self.activateWindow()  # Bring the window to the front
            else:
                self.showMinimized()

    @Slot()
    def close_main_window(self) -> None:
        """
        Slot that shows Confirmation Dialog to ask user to confirm they want to quit the application.

        Returns:
            None: This function does not return a value.
        """
        dialog = ConfirmationDialog(
            "Close Application?",
            "Are you sure you do want to close the application?",
            "Close",
        )
        self.send_logs.emit("Close Application Button Clicked", "INFO", True)
        if dialog.show():
            self.close()
        else:
            self.send_logs.emit("Cancelled Closing Application", "INFO", True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event to emit the shutdown signals and ensure the application closes properly.

        Args:
            event (QCloseEvent): The close event triggered when the user attempts to close the window.

        Returns:
            None: This function does not return a value.
        """
        self.send_logs.emit("Closing Application", "INFO", True)
        self.appshutdown.emit()
        event.accept()
