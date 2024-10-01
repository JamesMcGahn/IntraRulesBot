from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class IconOnlyNavBarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_only_widget_ui")

    def init_ui(self):
        self.setMaximumSize(QSize(70, 16777215))
        self.setMinimumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.icon_nav_vlayout = QVBoxLayout(self)
        self.icon_nav_vlayout.setObjectName("icon_nav_vlayout")
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ico")
        self.keys_btn_ico = QPushButton()
        self.keys_btn_ico.setObjectName("keys_btn_ico")
        icon = QIcon()
        icon.addFile(
            ":/images/key_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon.addFile(":/images/key_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.keys_btn_ico.setIcon(icon)
        self.keys_btn_ico.setIconSize(QSize(100, 20))
        self.keys_btn_ico.setCheckable(True)
        self.keys_btn_ico.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.keys_btn_ico)

        self.rules_btn_ico = QPushButton()
        self.rules_btn_ico.setObjectName("rules_btn_ico")
        icon1 = QIcon()
        icon1.addFile(
            ":/images/edit_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon1.addFile(
            ":/images/edit_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.rules_btn_ico.setIcon(icon1)
        self.rules_btn_ico.setIconSize(QSize(100, 20))
        self.rules_btn_ico.setCheckable(True)
        self.rules_btn_ico.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.rules_btn_ico)

        self.logs_btn_ico = QPushButton()
        self.logs_btn_ico.setObjectName("logs_btn_ico")
        icon2 = QIcon()
        icon2.addFile(
            ":/images/log_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon2.addFile(":/images/log_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.logs_btn_ico.setIcon(icon2)
        self.logs_btn_ico.setIconSize(QSize(100, 20))
        self.logs_btn_ico.setCheckable(True)
        self.logs_btn_ico.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.logs_btn_ico)

        self.icon_nav_vlayout.addLayout(self.icon_btn_layout)

        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_nav_vlayout.addItem(self.verticalSpacer_2)

        self.signout_btn_ico = QPushButton()
        self.signout_btn_ico.setObjectName("signout_btn_ico")
        icon5 = QIcon()
        icon5.addFile(
            ":/images/signout_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon5.addFile(
            ":/images/signout_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.signout_btn_ico.setIcon(icon5)
        self.signout_btn_ico.setIconSize(QSize(100, 20))
        self.signout_btn_ico.setCheckable(True)
        self.signout_btn_ico.setAutoExclusive(True)

        self.icon_nav_vlayout.addWidget(self.signout_btn_ico)
