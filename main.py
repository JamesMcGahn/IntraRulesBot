# import faulthandler
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
from views import MainWindow
from views.components.dialogs import LoadingDialog, MessageDialog
from context import AppContext
from app_styles_css import STYLES

# faulthandler.enable(file=sys.stderr)
# faulthandler.enable()


class ApplicationBootStrap(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.context: AppContext = AppContext()
        self.main_window: None | MainWindow = None

        self.startup_dialog = LoadingDialog(
            "App Loading", "Application loading... Please Wait."
        )
        self.context.start_up_completed.connect(self._handle_start_up_complete)

    def start_up(self):
        self.startup_dialog.show()
        self.context.start_up()

    def _handle_start_up_complete(self, success: bool):
        self.startup_dialog.set_allow_close(True)
        self.startup_dialog.close()

        if success:
            self.main_window = MainWindow(self.app, self.context)
            self.main_window.show()
        else:
            MessageDialog(
                "App Start Failed",
                "App Start Failed. Please review the application logs.",
            ).show()
            self.app.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES)
    app_boot = ApplicationBootStrap(app)
    app_boot.start_up()

    sys.exit(app.exec())
