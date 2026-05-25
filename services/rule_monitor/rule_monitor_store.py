from __future__ import annotations

from services.rule_runner.enums import RULEEXECSTATUS, RULERUNSTATUS

from .models import RuleRunRow, RunSummary


class RunMonitorStore:
    def __init__(self):
        self.rows: dict[str, RuleRunRow] = {}
        self.summary = RunSummary()

    def reset(self):
        self.rows.clear()
        self.summary = RunSummary()

    def upsert_row(self, row: RuleRunRow) -> RuleRunRow:
        old_row = self.rows.get(row.rule_guid, None)
        if old_row and row.started_at is None:
            row.started_at = old_row.started_at
        self.rows[row.rule_guid] = row
        self._recalculate_summary()

    def get_summary(self) -> RunSummary:
        return self.summary

    def _recalculate_summary(self) -> None:
        summary = RunSummary(total=len(self.rows))

        for row in self.rows.values():
            status_value = getattr(row.status, "value", row.status)

            if status_value in (RULEEXECSTATUS.SUCCESS, RULERUNSTATUS.SUCCESS):
                summary.succeeded += 1
                summary.completed += 1
            elif status_value in (
                RULERUNSTATUS.FAILED,
                RULEEXECSTATUS.BROWSER_ERROR,
                RULEEXECSTATUS.NAME_EXISTS_ERROR,
                RULEEXECSTATUS.UNKNOWN_ERROR,
                RULEEXECSTATUS.TIMEOUT_ERROR,
            ):
                summary.failed += 1
                summary.completed += 1
            elif status_value in (RULERUNSTATUS.RETRYING):
                summary.retrying += 1
            elif status_value in (
                RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                RULERUNSTATUS.STOPPED,
            ):
                summary.stopped += 1
                summary.completed += 1
            elif status_value in (RULEEXECSTATUS.PENDING, RULERUNSTATUS.PENDING):
                summary.pending += 1

        self.summary = summary
