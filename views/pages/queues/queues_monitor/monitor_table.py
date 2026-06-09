from time import time
from services.monitor.queue_monitor.models import QueueRunRow
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from dataclasses import fields
from datetime import datetime


class MonitorTableModel(QAbstractTableModel):

    def __init__(self, rows: list[QueueRunRow] | None = None):
        super().__init__()
        self.rule_rows: list[QueueRunRow] = rows if rows is not None else []
        self.row_by_guid: dict[str, int] = {
            row.queue_guid: index for index, row in enumerate(self.rule_rows)
        }

    def current_timestamp(self):
        return int(time())

    def rowCount(self, parent=None):
        return len(self.rule_rows)

    def columnCount(self, parent=None):
        return len(fields(QueueRunRow))

    def remove_selected(self, selected):
        indexes = [i.row() for i in selected]
        indexSet = set(indexes)
        filtered_list = [
            row for index, row in enumerate(self.rule_rows) if index not in indexSet
        ]
        self.update_data(filtered_list)

    def clear_model(self):
        self.update_data([])

    def update_data(self, rule_rows: list[QueueRunRow]):
        self.beginResetModel()
        self.rule_rows = rule_rows
        self.row_by_guid: dict[str, int] = {
            row.queue_guid: index for index, row in enumerate(self.rule_rows)
        }

        self.endResetModel()

    def upsert_row(self, rule_row: QueueRunRow) -> None:
        existing_index = self.row_by_guid.get(rule_row.queue_guid)

        if existing_index is not None:
            self.rule_rows[existing_index] = rule_row

            top_left = self.index(existing_index, 0)
            bottom_right = self.index(existing_index, self.columnCount() - 1)

            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            return

        row_index = len(self.rule_rows)

        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.rule_rows.append(rule_row)
        self.row_by_guid[rule_row.queue_guid] = row_index
        self.endInsertRows()

    def add_row(self, rule_row: QueueRunRow):
        row_index = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.rule_rows.append(rule_row)
        self.row_by_guid[rule_row.queue_guid] = row_index
        self.endInsertRows()

    def get_all_rows(self):
        return self.rule_rows

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Guid"
            if section == 1:
                return "Queue Row"
            if section == 2:
                return "Queue Name"
            if section == 3:
                return "Status"
            if section == 4:
                return "Task"
            if section == 5:
                return "Retry Count"
            if section == 6:
                return "Started At:"
            if section == 7:
                return "Finished At:"
            if section == 8:
                return "Message:"
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        rule_row = self.rule_rows[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return rule_row.queue_guid
            elif index.column() == 1:
                return rule_row.queue_row
            elif index.column() == 2:
                return rule_row.queue_name
            elif index.column() == 3:
                return rule_row.status.value if rule_row.status else ""
            elif index.column() == 4:
                return rule_row.task.value if rule_row.task else ""
            elif index.column() == 5:
                return rule_row.retry_count
            elif index.column() == 6:
                return self._format_time(rule_row.started_at)
            elif index.column() == 7:
                return self._format_time(rule_row.finished_at)
            elif index.column() == 8:
                return rule_row.message

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def _format_time(self, value):
        if value is None:
            return ""

        if isinstance(value, int):
            value = datetime.fromtimestamp(value)
            value = value.strftime("%H:%M:%S")

        return str(value)
