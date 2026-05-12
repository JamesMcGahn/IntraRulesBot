from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import BookmarksPageControllers
    from base.events import UIEvent
    from services.rule_sets.models import RuleSet

from base import QWidgetBase
from base.events import RuleSetsLoadedEvent


from PySide6.QtCore import Slot
from .bookmarks_page_css import STYLES
from .bookmarks_page_ui import BookMarksPageView


class BookMarksPage(QWidgetBase):
    """
    A controller class for managing the BookMarks page, which allows users to load and view default rulesets or rulesets they saved.
    """

    def __init__(self, controllers: BookmarksPageControllers):
        super().__init__()
        self.controllers = controllers
        self.rule_sets_controller = self.controllers.rule_sets

        self.setStyleSheet(STYLES)
        # Initialize the UI for the LogsPage
        self.ui = BookMarksPageView()
        self.layout.addWidget(self.ui)

        # Slots / Signals

        self.rule_sets_controller.ui_event.connect(self.receive_ui_event)

        self.ui.rule_set_editted.connect(self.handle_rule_set_editted)
        self.ui.rule_set_saved.connect(self.handle_rule_set_saved)
        self.ui.rule_set_delete.connect(self.handle_rule_set_deleted)
        self.ui.rule_set_load_editor.connect(self.handle_load_to_editor)

        self.check_for_saved_rule_sets()

    def check_for_saved_rule_sets(self) -> None:
        """
        Check if there are any saved rules and emit them to the view.
        """
        self.rule_sets_controller.hydrate_rule_set_page()

    @Slot(object)
    def handle_rule_set_editted(self, rule_set: RuleSet):
        self.rule_sets_controller.rule_set_edited(rule_set)

    @Slot(object)
    def receive_ui_event(self, event: UIEvent):
        if isinstance(event.payload, RuleSetsLoadedEvent):
            self.ui.rule_sets_changed(event.payload.rule_sets)

    @Slot(object, str)
    def handle_rule_set_saved(self, guid: str, file_path: str):
        self.rule_sets_controller.rule_set_to_file(guid, file_path)

    @Slot(object)
    def handle_rule_set_deleted(self, rule_set: RuleSet):
        self.rule_sets_controller.rule_set_delete(rule_set)

    @Slot()
    def handle_load_to_editor(self, guid: str):
        self.rule_sets_controller.load_to_editor(guid)
