from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .icon_text_navbar_css import STYLES
from .icon_text_navbar_ui import IconTextNavBarView


class IconTextNavBar(QWidget):
    btn_checked_ict = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self):
        super().__init__()

        self.setObjectName("icon_text_widget")
        self.setMaximumSize(QSize(250, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)

        self.ui = IconTextNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.keys_btn_ict.toggled.connect(self.btn_checked)
        self.ui.keys_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.rules_btn_ict.toggled.connect(self.btn_checked)
        self.ui.rules_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.logs_btn_ict.toggled.connect(self.btn_checked)
        self.ui.logs_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.signout_btn_ict.toggled.connect(self.btn_checked)
        self.ui.signout_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.rules_btn_ict.setChecked(True)
        self.setHidden(True)

    def btn_checked(self, checked):
        self.btn_checked_ict.emit(checked, self.sender())

    def btn_clicked(self):
        self.btn_clicked_page.emit(self.sender())

    @Slot(bool)
    def hide_nav(self, checked):
        self.setHidden(not checked)

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked, btn):
        match btn.objectName():
            case "keys_btn_ico":
                self.ui.keys_btn_ict.setChecked(checked)
            case "rules_btn_ico":
                self.ui.rules_btn_ict.setChecked(checked)
            case "logs_btn_ico":
                self.ui.logs_btn_ict.setChecked(checked)
            case "settings_btn_ico":
                self.ui.settings_btn_ict.setChecked(checked)
            case "signout_btn_ico":
                self.ui.signout_btn_ict.setChecked(checked)
