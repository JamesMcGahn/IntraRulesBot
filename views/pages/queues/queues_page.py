from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import QueuesPageControllers

from PySide6.QtCore import Signal, Slot
from views.components.toasts.qtoast.enums import QTOASTSTATUS

from base import QWidgetBase
from .queues_page_css import STYLES
from .queues_ui import QueuesPageView
from ...base.enums import MONITOREVENT
from .enums.queues_page_event import QUEUESPAGEEVENT
from .models.queues_page_action import QueuesPageAction
from base.events import (
    MonitorRowUpsertEvent,
    MonitorSummaryUpdateEvent,
    MonitorSnapShotEvent,
    UIEvent,
    QueueRunnerStateEvent,
    ProgressStatus,
)
from .queues_monitor.queues_runner_monitor import QueuesRunnerMonitor


class QueuesPage(QWidgetBase):
    """
    Queues page that integrates the UI view with the logic for
    """

    monitor_upsert_row = Signal(object)
    monitor_summary_update = Signal(object)
    progress_bar_update = Signal(int, int)
    queue_runner_state_update = Signal(object)
    monitor_snapshot_update = Signal(object)

    def __init__(self, controllers: QueuesPageControllers):
        super().__init__()
        self.controllers = controllers
        self.monitor_controller = controllers.monitor
        self.queues_controller = controllers.queues
        self.setStyleSheet(STYLES)
        # Initialize the view
        self.ui = QueuesPageView()
        self.layout.addWidget(self.ui)

        self.queues_controller.ui_event.connect(self.receive_ui_event)
        self.monitor_controller.ui_event.connect(self.receive_ui_event)

        self.queue_runner_monitor = QueuesRunnerMonitor(self)

        # UI Page connections
        self.ui.queues_page_action.connect(self.handle_queue_page_action)
        self.progress_bar_update.connect(self.ui.set_progress_bar)
        self.queue_runner_state_update.connect(self.ui.handle_queue_runner_state_update)

        # Monitor connections
        self.monitor_upsert_row.connect(self.queue_runner_monitor.handle_upsert_row)
        self.monitor_summary_update.connect(
            self.queue_runner_monitor.handle_summary_update
        )
        self.monitor_snapshot_update.connect(
            self.queue_runner_monitor.update_from_snapshot
        )
        self.queue_runner_monitor.monitor_action.connect(self.handle_monitor_actions)

    @Slot(object)
    def receive_ui_event(self, event: UIEvent):
        if isinstance(event.payload, MonitorRowUpsertEvent):
            self.monitor_upsert_row.emit(event.payload.row)
        elif isinstance(event.payload, MonitorSummaryUpdateEvent):

            self.monitor_summary_update.emit(event.payload.summary)
        elif isinstance(event.payload, MonitorSnapShotEvent):
            self.monitor_snapshot_update.emit(event.payload)
        elif isinstance(event.payload, QueueRunnerStateEvent):
            self.queue_runner_state_update.emit(event.payload.state)
        elif isinstance(event.payload, ProgressStatus):
            self.progress_bar_update.emit(
                event.payload.current_value, event.payload.total
            )

    def handle_monitor_actions(self, action: MONITOREVENT):
        if action == MONITOREVENT.MONITOR_CLEAR_ALL:
            self.monitor_controller.clear_all()
            return
        if action == MONITOREVENT.MONITOR_REMOVE_SUCCEED:
            self.monitor_controller.remove_succeed()

    @Slot(object)
    def handle_queue_page_action(self, action: QueuesPageAction):
        action_handlers = {
            QUEUESPAGEEVENT.START_RUNNER: self._handle_queue_runner_run,
            QUEUESPAGEEVENT.STOP_RUNNER: self._handle_rule_runner_stop,
            QUEUESPAGEEVENT.TOGGLE_DISPLAY_MONITOR: self._handle_display_monitor,
        }

        handler = action_handlers.get(action.event, None)
        if handler is None:
            return
        handler(action)

    def _handle_queue_runner_run(self, action: QueuesPageAction):
        self.controllers.queues.import_file(action.data)

    def _handle_rule_runner_stop(self, _) -> None:
        self.log_with_toast(
            "Stop Runner Requested",
            "Stopping Queue Runner.",
            "INFO",
            QTOASTSTATUS.WARNING,
        )
        self.controllers.queues.handle_stop_runner()

    def _handle_display_monitor(self, _) -> None:
        if self.queue_runner_monitor and self.queue_runner_monitor.isVisible():
            self.queue_runner_monitor.close()
            return
        if self.queue_runner_monitor and not self.queue_runner_monitor.isVisible():
            self.queue_runner_monitor.show()
            return
