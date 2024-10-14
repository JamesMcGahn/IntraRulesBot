from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.helpers import StyleHelper, WidgetFactory


class IconTextNavBarView(QWidget):
    """
    Expanded side navigation bar with both icons and text buttons.

    Attributes:
        keys_btn_ict (QPushButton): Button for login credentials section.
        rules_btn_ict (QPushButton): Button for rules section.
        logs_btn_ict (QPushButton): Button for logs section.
        settings_btn_ict (QPushButton): Button for settings section.
        signout_btn_ict (QPushButton): Button for exit/sign-out section.
    """

    def __init__(self):
        """
        Initializes the IconTextNavBarView UI, setting up the buttons and applying styles.
        """
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_text_widget_ui")

    def init_ui(self):
        """
        Creates and adds the UI components, including buttons with icons and text.
        Adds shadow effects to the buttons and ensures proper layout structure.

        Returns:
            None: This function does not return a value.
        """
        self.setMaximumSize(QSize(250, 16777215))

        StyleHelper.drop_shadow(self)

        self.setAttribute(Qt.WA_StyledBackground, True)
        # Layout for the navigation bar
        self.icon_text_nav_vlayout = QVBoxLayout(self)
        self.icon_text_nav_vlayout.setObjectName("icon_text_nav_vlayout")
        # Layout for the buttons
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ict")
        # Create the buttons with text and icons
        self.keys_btn_ict = QPushButton(" Login Creds")
        self.keys_btn_ict.setObjectName("keys_btn_ict")
        self.icon_btn_layout.addWidget(self.keys_btn_ict)

        self.rules_btn_ict = QPushButton(" Rules")
        self.rules_btn_ict.setObjectName("rules_btn_ict")
        self.icon_btn_layout.addWidget(self.rules_btn_ict)

        self.logs_btn_ict = QPushButton(" Logs")
        self.logs_btn_ict.setObjectName("logs_btn_ict")
        self.icon_btn_layout.addWidget(self.logs_btn_ict)

        self.icon_text_nav_vlayout.addLayout(self.icon_btn_layout)
        # Spacer to push settings and signout buttons to the bottom
        self.verticalSpacer_3 = QSpacerItem(
            20, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_text_nav_vlayout.addItem(self.verticalSpacer_3)
        # Settings and sign-out buttons
        self.settings_btn_ict = QPushButton("Settings")
        self.settings_btn_ict.setObjectName("settings_btn_ict")
        self.icon_text_nav_vlayout.addWidget(self.settings_btn_ict)

        self.signout_btn_ict = QPushButton("Exit")
        self.signout_btn_ict.setObjectName("signout_btn_ict")
        self.icon_text_nav_vlayout.addWidget(self.signout_btn_ict)

        icons = [
            (self.keys_btn_ict, ":/images/key_off.png", ":/images/key_on.png"),
            (self.rules_btn_ict, ":/images/edit_off.png", ":/images/edit_on.png"),
            (self.logs_btn_ict, ":/images/log_off.png", ":/images/log_on.png"),
            (
                self.settings_btn_ict,
                ":/images/settings_off.png",
                ":/images/settings_on.png",
            ),
            (
                self.signout_btn_ict,
                ":/images/signout_off.png",
                ":/images/signout_on.png",
            ),
        ]
        # Apply icons and styles to each button
        for icon in icons:
            parent, image_loc_1, image_loc_2 = icon
            WidgetFactory.create_icon(
                parent, image_loc_1, 100, 20, True, image_loc_2, True
            )
            StyleHelper.drop_shadow(parent)
