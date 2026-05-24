from __future__ import annotations

from .models import (
    RuleRunRow,
)


class RunMonitorStore:
    def __init__(self):
        self.rows: dict[str, RuleRunRow] = {}

    def reset(self):
        self.rows.clear()

    def upsert_row(self, row: RuleRunRow) -> RuleRunRow:
        old_row = self.rows.get(row.rule_guid, None)
        if old_row and row.started_at is None:
            row.started_at = old_row.started_at
        self.rows[row.rule_guid] = row
