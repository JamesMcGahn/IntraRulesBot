import faulthandler
import sys

faulthandler.enable(file=sys.stderr)

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

app = QApplication(sys.argv)


window = MainWindow(app)
window.show()
app.exec()
