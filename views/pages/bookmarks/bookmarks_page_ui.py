from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.buttons import EditorActionButton
from components.helpers import WidgetFactory


class BookMarksPageView(QWidget):
    """
    A UI component that represents the Bookmarks display page.

    Signals:


    Attributes:
    """

    delete_rule_set = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.rule_sets = []

    def init_ui(self) -> None:
        """
        Initializes the UI components of the Bookmarks page, including the layout and
        the text display for bookmarks.

        Returns:
            None: This function does not return a value.
        """
        self.rule_set_page_layout = QVBoxLayout(self)

        outter_layout = WidgetFactory.create_form_box(
            "Rule Sets",
            self.rule_set_page_layout,
            False,
            object_name="Rule-Sets",
            title_color="#fcfcfc",
        )

        inner_h_layout = QHBoxLayout()

        inner_layout = WidgetFactory.create_form_box(
            "",
            inner_h_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            max_width=400,
        )

        inner_h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        outter_layout.addRow(inner_h_layout)

        rule_set_widget = QWidget()
        rule_set_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        rule_set_widget.setObjectName("rule-set-widget")

        rule_set_layout = QVBoxLayout(rule_set_widget)
        h_layout = QHBoxLayout()

        self.arrow_up = EditorActionButton("")
        self.arrow_down = EditorActionButton("")
        WidgetFactory.create_icon(
            self.arrow_up,
            ":/images/up_arrow_off_b.png",
            25,
            20,
            True,
            ":/images/up_arrow_on.png",
            False,
        )
        WidgetFactory.create_icon(
            self.arrow_down,
            ":/images/down_arrow_off_b.png",
            25,
            20,
            True,
            ":/images/down_arrow_on.png",
            False,
        )
        # Nav Buttons
        nav_box = QVBoxLayout()
        nav_box.addWidget(self.arrow_up)
        nav_box.addWidget(self.arrow_down)

        h_layout.addLayout(nav_box)
        rule_set_layout.addLayout(h_layout)

        # List Widget
        self.list_widget = QListWidget()

        # Rule Set Details
        rule_set_details = QVBoxLayout()
        self.rule_set_name = QLineEdit()
        self.rule_set_description = QTextEdit()
        rule_set_details.addWidget(self.rule_set_name)
        rule_set_details.addWidget(self.rule_set_description)

        rule_set_layout.addLayout(rule_set_details)

        h_layout.addWidget(self.list_widget)

        # Action Buttons Bar
        action_btns_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete")
        action_btns_layout.addWidget(self.delete_button)

        rule_set_layout.addLayout(action_btns_layout)

        inner_layout.addRow(rule_set_widget)

        self.delete_button.clicked.connect(self.remove_item)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.arrow_up.clicked.connect(self.navigate_up)
        self.arrow_down.clicked.connect(self.navigate_down)

    def navigate_up(self):
        if self.list_widget.currentRow() > 0:
            self.list_widget.setCurrentRow(self.list_widget.currentRow() - 1)
        else:
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def navigate_down(self):
        print(self.list_widget.currentRow(), self.list_widget.count())
        if self.list_widget.currentRow() != self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(self.list_widget.currentRow() + 1)
        else:
            self.list_widget.setCurrentRow(0)

    def init_rule_set(self, rule_sets: list) -> None:

        for rule_set in rule_sets:
            self.add_rule_set(rule_set)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def on_selection_changed(self):
        print(self.list_widget.currentRow(), self.list_widget.count())
        list_item = self.list_widget.currentItem()
        list_item_id = list_item.data(Qt.UserRole)
        index = self.list_widget.currentRow()

        self.rule_set_name.setText(self.rule_sets[index]["name"])
        self.rule_set_description.setText(self.rule_sets[index]["description"])
        if list_item_id == "default":
            self.rule_set_name.setReadOnly(True)
            self.rule_set_description.setReadOnly(True)
        else:
            self.rule_set_name.setReadOnly(False)
            self.rule_set_description.setReadOnly(False)

    @Slot(object)
    def add_rule_set(self, rule_set: object) -> None:
        list_item = QListWidgetItem(rule_set["name"])
        list_item.setData(Qt.UserRole, rule_set["id"])
        self.list_widget.addItem(list_item)
        self.rule_sets.append(rule_set)

    def remove_item(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            id_selected = selected_item.data(Qt.UserRole)
            if id_selected == "default":
                print("cant delete default rule_sets")
            else:
                index = self.list_widget.currentRow()
                self.delete_rule_set.emit(id_selected)
                self.list_widget.takeItem(self.list_widget.row(selected_item))
                self.rule_sets.pop(index)
