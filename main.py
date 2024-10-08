# import faulthandler
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

app = QApplication(sys.argv)


# faulthandler.enable(file=sys.stderr)
# faulthandler.enable()
window = MainWindow(app)
window.show()
app.exec()
