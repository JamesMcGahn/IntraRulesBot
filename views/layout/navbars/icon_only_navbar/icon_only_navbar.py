from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from components.helpers import StyleHelper

from .icon_only_navbar_css import STYLES
from .icon_only_navbar_ui import IconOnlyNavBarView


class IconOnlyNavBar(QWidget):
    btn_checked_ico = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self):
        super().__init__()
        self.setObjectName("icon_only_widget")
        self.setMaximumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)

        self.ui = IconOnlyNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        StyleHelper.drop_shadow(self)

        self.ui.keys_btn_ico.toggled.connect(self.btn_checked)
        self.ui.keys_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.rules_btn_ico.toggled.connect(self.btn_checked)
        self.ui.rules_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.logs_btn_ico.toggled.connect(self.btn_checked)
        self.ui.logs_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.settings_btn_ico.toggled.connect(self.btn_checked)
        self.ui.settings_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.signout_btn_ico.toggled.connect(self.btn_checked)
        self.ui.signout_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.rules_btn_ico.setChecked(True)

    @Slot(bool)
    def hide_nav(self, checked):
        self.setHidden(checked)

    def btn_checked(self, checked):
        self.btn_checked_ico.emit(checked, self.sender())

    def btn_clicked(self):
        self.btn_clicked_page.emit(self.sender())

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked, btn):
        match btn.objectName():
            case "keys_btn_ict":
                self.ui.keys_btn_ico.setChecked(checked)
            case "rules_btn_ict":
                self.ui.rules_btn_ico.setChecked(checked)
            case "logs_btn_ict":
                self.ui.logs_btn_ico.setChecked(checked)
            case "settings_btn_ict":
                self.ui.settings_btn_ico.setChecked(checked)
            case "signout_btn_ict":
                self.ui.signout_btn_ico.setChecked(checked)
