from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from services.rule_runner.models import RuleProgressEvent
    from services.rule_monitor import RunMonitorStore

from services.rule_monitor.models import RuleRunRow
from PySide6.QtCore import Slot, Signal
from base import QObjectBase
from base.enums import UIEVENTTYPE
from base.events import (
    UIEvent,
    MonitorRowUpsertEvent,
)

# TODO Create Rule Runner Response


class RulesRunMonitorController(QObjectBase):
    ui_event = Signal(object)

    def __init__(self, run_store: RunMonitorStore):
        super().__init__()
        self.run_store = run_store

    @Slot(object)
    def handle_task_progress_event(self, event: RuleProgressEvent):
        print("**** controller", event)
        row = RuleRunRow(
            rule_guid=event.rule_guid,
            rule_name=event.rule_name,
            status=event.status,
            scope=event.task_ref.scope if event.task_ref else "",
            task=event.task_ref.task if event.task_ref else "",
            index=event.task_ref.index if event.task_ref else 0,
            detail_type=event.task_ref.detail_type if event.task_ref else "",
            message=event.message,
        )
        self.run_store.upsert_row(row)
        self._emit_row_updated(row)

    def _emit_row_updated(self, row):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=MonitorRowUpsertEvent(row=row),
            )
        )
