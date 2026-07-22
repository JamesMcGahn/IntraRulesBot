from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from services.queue_runner.models import QueueProgressEvent
    from services.monitor.queue_monitor import QueueMonitorStore
    from services.logger.adapters import LogAdapter

from PySide6.QtCore import Signal, Slot

from base.enums import UIEVENTTYPE
from base.events import (
    MonitorRowUpsertEvent,
    MonitorSummaryUpdateEvent,
    MonitorSnapShotEvent,
    ProgressStatus,
    UIEvent,
)
from services.monitor.queue_monitor.models import QueueRunRow
from services.monitor.models import RunSummary
from services.queue_runner.enums import QUEUERUNNERLIFECYCLE
from base import ControllerBase


class QueuesRunMonitorController(ControllerBase):
    request_remove = Signal(list)
    snapshot_update = Signal(list)

    def __init__(self, logger: LogAdapter, run_store: QueueMonitorStore):
        super().__init__(logger)
        self.run_store = run_store

    # FROM RULERUNNER
    def handle_runner_lifecyle(self, status: QUEUERUNNERLIFECYCLE):
        pass

    @Slot(object)
    def handle_task_progress_event(self, event: QueueProgressEvent):
        row = QueueRunRow(
            queue_guid=event.queue_guid,
            queue_row=event.queue_row,
            queue_name=event.queue_name,
            status=event.status,
            task=event.task,
            message=event.message,
            started_at=event.started_at,
            finished_at=event.finished_at,
        )
        self.run_store.upsert_row(row)
        self._emit_row_updated(row)
        self._emit_summary_updated(self.run_store.get_summary())

    def _emit_row_updated(self, row: QueueRunRow):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=MonitorRowUpsertEvent[QueueRunRow](row=row),
            )
        )

    def progress_status_event(self, value: int, total: int):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY, payload=ProgressStatus(value, total)
            )
        )

    def _emit_summary_updated(self, summary: RunSummary):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=MonitorSummaryUpdateEvent(summary=summary),
            )
        )

    def _emit_snap_shot(self, summary: RunSummary, rows: list[QueueRunRow]):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=MonitorSnapShotEvent[QueueRunRow](summary=summary, rows=rows),
            )
        )

    def clear_all(self):
        self.run_store.reset()
        self._emit_snap_shot(self.run_store.get_summary(), [])

    def remove_succeed(self):
        succeed_guids = self.run_store.remove_succeeded()
        snap_shot = self.run_store.get_rows_snapshot()
        self.request_remove.emit(succeed_guids)
        self._emit_snap_shot(self.run_store.get_summary(), snap_shot)
