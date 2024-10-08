from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.buttons import GradientButton
from components.helpers import StyleHelper, WidgetFactory


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
        StyleHelper.drop_shadow(self.app_logo)
        self.app_logo_vlayout.addWidget(self.app_logo)

        self.horizontalSpacer_3 = QSpacerItem(
            558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.inner_cont_hlayout.addLayout(self.app_logo_vlayout)
        self.inner_cont_hlayout.addItem(self.horizontalSpacer_3)

        self.open_file_btn = GradientButton(
            "Open File",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )

        self.open_file_btn.setMaximumWidth(100)
        self.open_file_btn.setMaximumHeight(30)

        self.inner_cont_hlayout.addWidget(self.open_file_btn)

        self.hamburger_icon_btn = QPushButton(self)
        StyleHelper.drop_shadow(self.hamburger_icon_btn)
        self.hamburger_icon_btn.setObjectName("hamburger-icon-btn")
        self.hamburger_icon_btn.setStyleSheet(
            "QPushButton {\n" "border: none;\n" "padding-right:.5em\n" "}"
        )

        WidgetFactory.create_icon(
            self.hamburger_icon_btn,
            ":/images/hamburger_off.png",
            29,
            35,
            True,
            ":/images/hamburger_on.png",
            False,
        )

        self.inner_cont_hlayout.addWidget(self.hamburger_icon_btn)

        self.navbar_vlayout.addLayout(self.inner_cont_hlayout)
