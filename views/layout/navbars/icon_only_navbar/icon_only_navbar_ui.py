from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from views.components.helpers import WidgetFactory
from ....base.enums import PAGE


class IconOnlyNavBarView(QWidget):
    """
    A compressed side navigation bar with icon-only buttons. This navigation bar includes buttons for keys, rules, logs,
    settings, and sign-out, each with corresponding icons that change on hover or click.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_only_widget_ui")

    def init_ui(self) -> None:
        """
        Initializes the UI components, including buttons and icons, for the side navigation bar.
        """
        self.setMaximumSize(QSize(70, 16777215))
        self.setMinimumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        # Main layout for the icon navigation bar
        self.icon_nav_vlayout = QVBoxLayout(self)
        self.icon_nav_vlayout.setObjectName("icon_nav_vlayout")
        # Layout for the icon buttons
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ico")
        # Create buttons for the navigation items

        self.rules_btn_ico = QPushButton()
        self.rules_btn_ico.setObjectName(PAGE.EDITOR)
        self.icon_btn_layout.addWidget(self.rules_btn_ico)

        self.logs_btn_ico = QPushButton()
        self.logs_btn_ico.setObjectName(PAGE.LOG)
        self.icon_btn_layout.addWidget(self.logs_btn_ico)

        self.bookmarks_btn_ico = QPushButton()
        self.bookmarks_btn_ico.setObjectName(PAGE.BOOKMARK)
        self.icon_btn_layout.addWidget(self.bookmarks_btn_ico)

        self.settings_btn_ico = QPushButton()
        self.settings_btn_ico.setObjectName(PAGE.SETTINGS)

        self.signout_btn_ico = QPushButton()
        self.signout_btn_ico.setObjectName(PAGE.EXIT)

        icons = [
            (self.rules_btn_ico, ":/images/edit_off.png", ":/images/edit_on.png"),
            (self.logs_btn_ico, ":/images/log_off.png", ":/images/log_on.png"),
            (
                self.bookmarks_btn_ico,
                ":/images/bookmark_off.png",
                ":/images/bookmark_on.png",
            ),
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
        # Create icons for each button
        for icon in icons:
            parent, image_loc_1, image_loc_2 = icon
            WidgetFactory.create_icon(
                parent, image_loc_1, 100, 20, True, image_loc_2, True
            )

        self.icon_nav_vlayout.addLayout(self.icon_btn_layout)
        # Spacer to push the settings and signout buttons to the bottom
        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_nav_vlayout.addItem(self.verticalSpacer_2)
        # Add settings and sign-out buttons at the bottom
        self.icon_nav_vlayout.addWidget(self.settings_btn_ico)
        self.icon_nav_vlayout.addWidget(self.signout_btn_ico)
