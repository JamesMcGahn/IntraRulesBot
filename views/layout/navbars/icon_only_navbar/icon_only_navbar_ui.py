from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.helpers import WidgetFactory


class IconOnlyNavBarView(QWidget):
    """Compressed Side Navigation Bar - Icon Only Buttons - UI Components"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_only_widget_ui")

    def init_ui(self):
        """Add UI Components"""
        self.setMaximumSize(QSize(70, 16777215))
        self.setMinimumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.icon_nav_vlayout = QVBoxLayout(self)
        self.icon_nav_vlayout.setObjectName("icon_nav_vlayout")
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ico")

        self.keys_btn_ico = QPushButton()
        self.keys_btn_ico.setObjectName("keys_btn_ico")
        self.icon_btn_layout.addWidget(self.keys_btn_ico)

        self.rules_btn_ico = QPushButton()
        self.rules_btn_ico.setObjectName("rules_btn_ico")
        self.icon_btn_layout.addWidget(self.rules_btn_ico)

        self.logs_btn_ico = QPushButton()
        self.logs_btn_ico.setObjectName("logs_btn_ico")
        self.icon_btn_layout.addWidget(self.logs_btn_ico)

        self.settings_btn_ico = QPushButton()
        self.settings_btn_ico.setObjectName("settings_btn_ico")

        self.signout_btn_ico = QPushButton()
        self.signout_btn_ico.setObjectName("signout_btn_ico")

        icons = [
            (self.keys_btn_ico, ":/images/key_off.png", ":/images/key_on.png"),
            (self.rules_btn_ico, ":/images/edit_off.png", ":/images/edit_on.png"),
            (self.logs_btn_ico, ":/images/log_off.png", ":/images/log_on.png"),
            (
                self.settings_btn_ico,
                ":/images/settings_off.png",
                ":/images/settings_on.png",
            ),
            (
                self.signout_btn_ico,
                ":/images/signout_off.png",
                ":/images/signout_on.png",
            ),
        ]

        for icon in icons:
            parent, image_loc_1, image_loc_2 = icon
            WidgetFactory.create_icon(
                parent, image_loc_1, 100, 20, True, image_loc_2, True
            )

        self.icon_nav_vlayout.addLayout(self.icon_btn_layout)

        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_nav_vlayout.addItem(self.verticalSpacer_2)

        self.icon_nav_vlayout.addWidget(self.settings_btn_ico)
        self.icon_nav_vlayout.addWidget(self.signout_btn_ico)
