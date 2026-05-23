from PySide6.QtCore import QSize, Qt, Signal
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

    page_change_request = Signal(object)

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

        top_buttons = [
            (
                PAGE.EDITOR,
                self.icon_btn_layout,
                ":/images/edit_off.png",
                ":/images/edit_on.png",
            ),
            (
                PAGE.LOG,
                self.icon_btn_layout,
                ":/images/log_off.png",
                ":/images/log_on.png",
            ),
            (
                PAGE.BOOKMARK,
                self.icon_btn_layout,
                ":/images/bookmark_off.png",
                ":/images/bookmark_on.png",
            ),
        ]

        lower_buttons = [
            (
                PAGE.SETTINGS,
                self.icon_nav_vlayout,
                ":/images/settings_off.png",
                ":/images/settings_on.png",
            ),
            (
                PAGE.EXIT,
                self.icon_nav_vlayout,
                ":/images/signout_off.png",
                ":/images/signout_on.png",
            ),
        ]

        self.set_up_page_buttons(top_buttons)

        self.icon_nav_vlayout.addLayout(self.icon_btn_layout)
        # Spacer to push the settings and signout buttons to the bottom
        self.set_up_spacers()

        self.set_up_page_buttons(lower_buttons)

    def set_up_page_buttons(self, data: tuple):
        for button_info in data:
            parent, layout, image_loc_1, image_loc_2 = button_info

            setattr(self, parent, QPushButton())
            btn: QPushButton = getattr(self, parent)
            btn.setObjectName(parent)
            btn.clicked.connect(self._btn_clicked)
            # btn.toggled.connect(self._btn_checked)
            layout.addWidget(btn)
            WidgetFactory.create_icon(
                btn, image_loc_1, 100, 20, True, image_loc_2, True
            )

    def set_up_spacers(self):
        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_nav_vlayout.addItem(self.verticalSpacer_2)

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
