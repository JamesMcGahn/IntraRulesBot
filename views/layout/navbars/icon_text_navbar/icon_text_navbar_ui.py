from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from views.components.helpers import StyleHelper, WidgetFactory

from ....base.enums import PAGE


class IconTextNavBarView(QWidget):
    """
    Expanded side navigation bar with both icons and text buttons.
    """

    page_change_request = Signal(object)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_text_widget_ui")

    def init_ui(self):
        """
        Creates and adds the UI components, including buttons with icons and text.
        Adds shadow effects to the buttons and ensures proper layout structure.
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
        self.icon_text_nav_vlayout.addLayout(self.icon_btn_layout)
        top_buttons = [
            (
                PAGE.EDITOR,
                " Rules",
                self.icon_btn_layout,
                ":/images/edit_off.png",
                ":/images/edit_on.png",
            ),
            (
                PAGE.LOG,
                " Logs",
                self.icon_btn_layout,
                ":/images/log_off.png",
                ":/images/log_on.png",
            ),
            (
                PAGE.BOOKMARK,
                " Rule Sets",
                self.icon_btn_layout,
                ":/images/bookmark_off.png",
                ":/images/bookmark_on.png",
            ),
            (
                PAGE.QUEUES,
                " Queues",
                self.icon_btn_layout,
                ":/images/queues_off.png",
                ":/images/queues_on.png",
            ),
        ]

        lower_buttons = [
            (
                PAGE.SETTINGS,
                "Settings",
                self.icon_text_nav_vlayout,
                ":/images/settings_off.png",
                ":/images/settings_on.png",
            ),
            (
                PAGE.EXIT,
                "Exit",
                self.icon_text_nav_vlayout,
                ":/images/signout_off.png",
                ":/images/signout_on.png",
            ),
        ]
        self.set_up_page_buttons(top_buttons)
        self.set_up_spacers()
        self.set_up_page_buttons(lower_buttons)

    def set_up_page_buttons(self, data: tuple):
        for button_info in data:
            parent, label_name, layout, image_loc_1, image_loc_2 = button_info

            setattr(self, parent, QPushButton(label_name))
            btn: QPushButton = getattr(self, parent)
            btn.setObjectName(parent)
            btn.clicked.connect(self._btn_clicked)
            # btn.toggled.connect(self._btn_checked)
            layout.addWidget(btn)
            WidgetFactory.create_icon(
                btn, image_loc_1, 100, 20, True, image_loc_2, True
            )
            StyleHelper.drop_shadow(btn)

    def set_up_spacers(self):
        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_text_nav_vlayout.addItem(self.verticalSpacer_2)

    def _btn_clicked(self) -> None:
        """
        Handles the button click event and emits the `btn_clicked_page` signal.
        """
        self.page_change_request.emit(PAGE(self.sender().objectName()))

    def _btn_checked(self, checked: bool) -> None:
        """
        Handles the button toggle state and emits the `btn_checked_ict` signal.
        """
        if checked:
            self.page_change_request.emit(PAGE(self.sender().objectName()))

    def sync_page(self, page_name: PAGE) -> None:
        btn = getattr(self, page_name)
        if btn:
            btn.setChecked(True)
