from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class IconTextNavBarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_text_widget_ui")

    def init_ui(self):
        self.setMaximumSize(QSize(250, 16777215))

        self.setAttribute(Qt.WA_StyledBackground, True)
        icon = QIcon()
        icon.addFile(
            ":/images/key_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon.addFile(":/images/key_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)

        icon1 = QIcon()
        icon1.addFile(
            ":/images/edit_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon1.addFile(
            ":/images/edit_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon2 = QIcon()
        icon2.addFile(
            ":/images/log_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon2.addFile(":/images/log_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon4 = QIcon()
        icon4.addFile(
            ":/images/settings_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon4.addFile(
            ":/images/settings_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon5 = QIcon()
        icon5.addFile(
            ":/images/signout_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon5.addFile(
            ":/images/signout_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.icon_text_nav_vlayout = QVBoxLayout(self)
        self.icon_text_nav_vlayout.setObjectName("icon_text_nav_vlayout")
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ict")
        self.keys_btn_ict = QPushButton(self)
        self.keys_btn_ict.setObjectName("keys_btn_ict")
        self.keys_btn_ict.setIcon(icon)
        self.keys_btn_ict.setIconSize(QSize(100, 20))
        self.keys_btn_ict.setCheckable(True)
        self.keys_btn_ict.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.keys_btn_ict)

        self.rules_btn_ict = QPushButton(self)
        self.rules_btn_ict.setObjectName("rules_btn_ict")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.rules_btn_ict.sizePolicy().hasHeightForWidth()
        )
        self.rules_btn_ict.setSizePolicy(sizePolicy1)
        self.rules_btn_ict.setMaximumSize(QSize(16777215, 16777215))
        self.rules_btn_ict.setIcon(icon1)
        self.rules_btn_ict.setIconSize(QSize(100, 20))
        self.rules_btn_ict.setCheckable(True)
        self.rules_btn_ict.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.rules_btn_ict)

        self.logs_btn_ict = QPushButton(self)
        self.logs_btn_ict.setObjectName("logs_btn_ict")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.logs_btn_ict.sizePolicy().hasHeightForWidth()
        )
        self.logs_btn_ict.setSizePolicy(sizePolicy2)
        self.logs_btn_ict.setIcon(icon2)
        self.logs_btn_ict.setIconSize(QSize(100, 20))
        self.logs_btn_ict.setCheckable(True)
        self.logs_btn_ict.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.logs_btn_ict)

        self.icon_text_nav_vlayout.addLayout(self.icon_btn_layout)

        self.verticalSpacer_3 = QSpacerItem(
            20, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_text_nav_vlayout.addItem(self.verticalSpacer_3)

        self.settings_btn_ict = QPushButton(self)
        self.settings_btn_ict.setObjectName("settings_btn_ict")
        self.settings_btn_ict.setIcon(icon4)
        self.settings_btn_ict.setIconSize(QSize(100, 20))
        self.settings_btn_ict.setCheckable(True)
        self.settings_btn_ict.setAutoExclusive(True)

        self.signout_btn_ict = QPushButton(self)
        self.signout_btn_ict.setObjectName("signout_btn_ict")
        self.signout_btn_ict.setIcon(icon5)
        self.signout_btn_ict.setIconSize(QSize(100, 20))
        self.signout_btn_ict.setCheckable(True)
        self.signout_btn_ict.setAutoExclusive(True)

        self.keys_btn_ict.setText(" Login Creds")
        self.rules_btn_ict.setText(" Rules")
        self.logs_btn_ict.setText(" Logs")
        self.settings_btn_ict.setText("Settings")
        self.signout_btn_ict.setText("Exit")

        self.icon_text_nav_vlayout.addWidget(self.settings_btn_ict)
        self.icon_text_nav_vlayout.addWidget(self.signout_btn_ict)
