from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import QueuesPageControllers

from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from .queues_page_css import STYLES
from .queues_ui import QueuesPageView

from .enums.queues_page_event import QUEUESPAGEEVENT
from .models.queues_page_action import QueuesPageAction


class QueuesPage(QWidgetBase):
    """
    Queues page that integrates the UI view with the logic for
    """

    def __init__(self, controllers: QueuesPageControllers):
        super().__init__()
        self.controllers = controllers

        self.setStyleSheet(STYLES)
        # Initialize the view
        self.ui = QueuesPageView()
        self.layout.addWidget(self.ui)

        self.ui.queues_page_action.connect(self.handle_rule_page_action)

    @Slot(object)
    def handle_rule_page_action(self, action: QueuesPageAction) -> None:
        print(action)
