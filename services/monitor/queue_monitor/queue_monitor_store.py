from __future__ import annotations

from services.queue_runner.enums import QUEUEEXECSTATUS, QUEUERUNSTATUS

from .models import QueueRunRow
from services.monitor.models import RunSummary


class QueueMonitorStore:
    def __init__(self):
        self.rows: dict[str, QueueRunRow] = {}
        self.summary = RunSummary()

    def reset(self):
        self.rows.clear()
        self.summary = RunSummary()

    def upsert_row(self, row: QueueRunRow) -> QueueRunRow:
        old_row = self.rows.get(row.queue_guid, None)
        if old_row and row.started_at is None:
            row.started_at = old_row.started_at
        self.rows[row.queue_guid] = row
        self._recalculate_summary()

    def get_summary(self) -> RunSummary:
        return self.summary

    def get_rows_snapshot(self) -> list[QueueRunRow]:
        return list(self.rows.values())

    def _recalculate_summary(self) -> None:
        summary = RunSummary(total=len(self.rows))

        for row in self.rows.values():
            status_value = getattr(row.status, "value", row.status)

            if status_value in (QUEUEEXECSTATUS.SUCCESS, QUEUERUNSTATUS.SUCCESS):
                summary.succeeded += 1
                summary.completed += 1
            elif status_value in (
                QUEUERUNSTATUS.FAILED,
                QUEUEEXECSTATUS.BROWSER_ERROR,
                QUEUEEXECSTATUS.NAME_EXISTS_ERROR,
                QUEUEEXECSTATUS.UNKNOWN_ERROR,
                QUEUEEXECSTATUS.TIMEOUT_ERROR,
            ):
                summary.failed += 1
                summary.completed += 1
            elif status_value in (QUEUERUNSTATUS.RETRYING):
                summary.retrying += 1
            elif status_value in (
                QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR,
                QUEUERUNSTATUS.STOPPED,
            ):
                summary.stopped += 1
                summary.completed += 1
            elif status_value in (QUEUEEXECSTATUS.PENDING, QUEUERUNSTATUS.PENDING):
                summary.pending += 1

        self.summary = summary

    def remove_succeeded(self) -> list[str]:
        succeed = []
        for row in self.rows.values():
            if (
                row.status == QUEUEEXECSTATUS.SUCCESS
                or row.status == QUEUERUNSTATUS.SUCCESS
            ):
                succeed.append(row.queue_guid)

        for guid in succeed:
            self.rows.pop(guid)
        self._recalculate_summary()
        return succeed
