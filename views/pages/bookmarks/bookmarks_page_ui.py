from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rule_sets.models import RuleSet


from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from views.components.buttons import EditorActionButton, GradientButton
from views.components.helpers import WidgetFactory


class BookMarksPageView(QWidget):
    """
    A UI component that represents the Bookmarks display page.
    """

    rule_set_editted = Signal(object)
    rule_set_saved = Signal(object, str)
    rule_set_delete = Signal(object)
    rule_set_load_editor = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.rule_sets: list[RuleSet] = []
        self.current_index = 0

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
            max_width=500,
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
        self.arrow_down.setCursor(Qt.PointingHandCursor)
        self.arrow_up.setCursor(Qt.PointingHandCursor)
        WidgetFactory.create_icon(
            self.arrow_up,
            ":/images/up_arrow_off_b.png",
            49,
            20,
            True,
            ":/images/up_arrow_on.png",
            False,
        )
        WidgetFactory.create_icon(
            self.arrow_down,
            ":/images/down_arrow_off_b.png",
            49,
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
        details_layout = QFormLayout()
        details_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.selected_rule_set_name = QLineEdit()
        self.selected_rule_set_description = QTextEdit()
        self.selected_rule_set_name_label = QLabel("Name:")
        self.selected_rule_set_name_label.setAlignment(Qt.AlignLeft)
        self.selected_rule_set_description_label = QLabel("Description:")
        self.selected_rule_set_description_label.setAlignment(Qt.AlignLeft)

        details_layout.addRow(
            self.selected_rule_set_name_label, self.selected_rule_set_name
        )
        details_layout.addRow(
            self.selected_rule_set_description_label, self.selected_rule_set_description
        )

        rule_set_layout.addLayout(details_layout)

        h_layout.addWidget(self.list_widget)

        # Action Buttons Bar
        action_btns_layout = QHBoxLayout()

        self.delete_button = GradientButton(
            "Delete",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.load_button = GradientButton(
            "Load to Editor",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.save_to_file_button = GradientButton(
            "Save to File",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )
        self.edit_details_button = GradientButton(
            "Update Details",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )

        action_btns_layout.addWidget(self.load_button)
        action_btns_layout.addWidget(self.save_to_file_button)
        action_btns_layout.addWidget(self.edit_details_button)
        action_btns_layout.addWidget(self.delete_button)

        rule_set_layout.addLayout(action_btns_layout)

        inner_layout.addRow(rule_set_widget)

        # SLOTS / SIGNALS

        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.arrow_up.clicked.connect(self.on_navigate_up)
        self.arrow_down.clicked.connect(self.on_navigate_down)
        self.delete_button.clicked.connect(self.handle_remove_rule_set)
        self.load_button.clicked.connect(self.handle_load_to_editor)
        self.save_to_file_button.clicked.connect(self.handle_save_rule_set_to_file)
        self.edit_details_button.clicked.connect(self.handle_update_rule_set_detail)

    def on_navigate_up(self):
        """
        Moves the selection up in the rule set list.
        If at the top, it moves selection to the last item in the list
        """

        if self.list_widget.currentRow() > 0:
            self.current_index = self.list_widget.currentRow() - 1
            self.list_widget.setCurrentRow(self.current_index)
        else:
            self.current_index = self.list_widget.count() - 1
            self.list_widget.setCurrentRow(self.current_index)

    def on_navigate_down(self):
        """
        Moves the selection down in the rule set list.
        If at the bottom, it moves selection to the first item in the list
        """
        if self.list_widget.currentRow() != self.list_widget.count() - 1:
            self.current_index = self.list_widget.currentRow() + 1
            self.list_widget.setCurrentRow(self.current_index)
        else:
            self.current_index = 0
            self.list_widget.setCurrentRow(self.current_index)

    def rule_sets_changed(self, rule_sets: list[RuleSet]):
        self.list_widget.blockSignals(True)
        self.clear_rule_sets()

        for rule_set in rule_sets:
            self._add_rule_set(rule_set)
        self.list_widget.blockSignals(False)
        if not len(rule_sets) > 0:
            return

        if self.current_index < len(rule_sets):

            self.list_widget.setCurrentRow(self.current_index)
        else:
            self.list_widget.setCurrentRow(0)

    def clear_rule_sets(self):
        self.list_widget.clear()
        self.rule_sets.clear()

    @Slot()
    def on_selection_changed(self):
        """
        Slot for handling the selection change in the rule set list.
        Updates the rule set details UI elements based on the selected rule set.
        """

        if not self.rule_sets:
            return
        self.current_index = self.list_widget.currentRow()
        rule_set = self.rule_sets[self.current_index]
        self.selected_rule_set_name.setText(rule_set.rule_set_name)
        self.selected_rule_set_description.setText(rule_set.description)
        if rule_set.default:
            self.selected_rule_set_name.setReadOnly(True)
            self.selected_rule_set_description.setReadOnly(True)
        else:
            self.selected_rule_set_name.setReadOnly(False)
            self.selected_rule_set_description.setReadOnly(False)

    def _add_rule_set(self, rule_set: RuleSet) -> None:
        """
        adding a rule set to the list of rules
        """
        list_item = QListWidgetItem(rule_set.rule_set_name)
        list_item.setData(Qt.UserRole, rule_set.guid)
        self.list_widget.addItem(list_item)
        self.rule_sets.append(rule_set)

    def handle_load_to_editor(self):
        index = self.list_widget.currentRow()
        rule_set = self.rule_sets[index]
        self.rule_set_load_editor.emit(rule_set.guid)

    def handle_remove_rule_set(self):
        """
        Slot for removing a rule set from the list of rule sets in the GUI and emits signal to remove from model
        If rule set is a default rule set, rule set is not removed
        """
        index = self.list_widget.currentRow()
        rule_set = self.rule_sets[index]
        self.rule_set_delete.emit(rule_set)

    def handle_update_rule_set_detail(self) -> None:
        """
        Update the rule set details in the GUI and emits signal to update rule set in the model.
        If rule set is a default rule set, rule set details are not updated
        """

        index = self.list_widget.currentRow()
        rule_set = self.rule_sets[index]

        if not rule_set.default:
            index = self.list_widget.currentRow()
            rule_set = self.rule_sets[index]

            self.rule_sets[index].rule_set_name = self.selected_rule_set_name.text()
            self.rule_sets[index].description = (
                self.selected_rule_set_description.toPlainText()
            )

        self.rule_set_editted.emit(rule_set)

    def handle_save_rule_set_to_file(self) -> None:
        """
        Save the selected rule set to a JSON file selected by the user. It ensures the file has
        a `.json` extension.
        """

        if not self.rule_sets:
            return

        index = self.list_widget.currentRow()
        rule_set = self.rule_sets[index]

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save JSON File",
            f"{rule_set.rule_set_name}.json",
            "JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return
            # Ensure the file has a .json extension
        if not file_path.endswith(".json"):
            file_path += ".json"
        self.rule_set_saved.emit(rule_set.guid, file_path)
