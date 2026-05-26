from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from services.rule_runner.models import RuleProgressEvent
    from services.rule_monitor import RunMonitorStore

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from base.enums import UIEVENTTYPE
from base.events import (
    MonitorRowUpsertEvent,
    MonitorSummaryUpdateEvent,
    UIEvent,
)
from services.rule_monitor.models import RuleRunRow, RunSummary
from services.rule_runner.enums import RULERUNNERLIFECYCLE


class RulesRunMonitorController(QObjectBase):
    ui_event = Signal(object)

    def __init__(self, run_store: RunMonitorStore):
        super().__init__()
        self.run_store = run_store

    # FROM RULERUNNER
    def handle_runner_lifecyle(self, status: RULERUNNERLIFECYCLE):
        pass

    @Slot(object)
    def handle_task_progress_event(self, event: RuleProgressEvent):
        row = RuleRunRow(
            rule_guid=event.rule_guid,
            rule_name=event.rule_name,
            status=event.status,
            scope=event.task_ref.scope if event.task_ref else "",
            task=event.task_ref.task if event.task_ref else "",
            index=event.task_ref.index if event.task_ref else 0,
            detail_type=event.task_ref.detail_type if event.task_ref else "",
            message=event.message,
            started_at=event.started_at,
            finished_at=event.finished_at,
        )
        self.run_store.upsert_row(row)
        self._emit_row_updated(row)
        self._emit_summary_updated(self.run_store.get_summary())

    def _emit_row_updated(self, row):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=MonitorRowUpsertEvent(row=row),
            )
        )

    def _emit_summary_updated(self, summary: RunSummary):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=MonitorSummaryUpdateEvent(summary=summary),
            )
        )
