from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class HeaderNavBarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("header_widget_ui")

        self.navbar_vlayout = QVBoxLayout(self)
        self.navbar_vlayout.setObjectName("navbar_vlayout")

        self.inner_cont_hlayout = QHBoxLayout()
        self.inner_cont_hlayout.setObjectName("inner_cont_hlayout")

        self.app_logo_vlayout = QVBoxLayout()
        self.app_logo_vlayout.setObjectName("app_logo_vlayout")

        self.app_logo = QLabel(self)
        self.app_logo.setObjectName("app_logo")
        self.app_logo.setStyleSheet("text-align: right;")
        original_pixmap = QPixmap(":/images/logo.png")

        self.app_logo.setPixmap(original_pixmap)

        self.app_logo_vlayout.addWidget(self.app_logo)

        self.horizontalSpacer_3 = QSpacerItem(
            558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.inner_cont_hlayout.addLayout(self.app_logo_vlayout)
        self.inner_cont_hlayout.addItem(self.horizontalSpacer_3)

        self.open_file_btn = QPushButton("Open File")

        self.inner_cont_hlayout.addWidget(self.open_file_btn)

        self.hamburger_icon_btn = QPushButton(self)
        self.hamburger_icon_btn.setObjectName("hamburger-icon-btn")
        self.hamburger_icon_btn.setStyleSheet(
            "QPushButton {\n" "border: none;\n" "padding-right:.5em\n" "}"
        )
        icon6 = QIcon()
        icon6.addFile(
            ":/images/hamburger_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon6.addFile(
            ":/images/hamburger_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.hamburger_icon_btn.setIcon(icon6)
        self.hamburger_icon_btn.setIconSize(QSize(29, 35))
        self.hamburger_icon_btn.setCheckable(True)

        self.inner_cont_hlayout.addWidget(self.hamburger_icon_btn)

        self.navbar_vlayout.addLayout(self.inner_cont_hlayout)
