from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from services.files.models import ImportedSheetsRow
from base import ServiceBase
from .models import Queue
from uuid import uuid4


class QueueBuilder(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)

    def build_queue(self, queue: ImportedSheetsRow) -> Queue:
        queue_name = queue.values.get("queue_name", "").strip()
        queue_number = queue.values.get("queue_number", "").strip()
        queue_row = queue.row_number

        if not queue_name or not queue_number:
            msg = f"Queue {queue_row} doesn't have value for both Queue Name & Queue Number."
            self._logging(msg, "ERROR")
            raise ValueError(msg)
        return Queue(
            guid=str(uuid4()),
            queue_name=queue_name,
            queue_number=queue_number,
            row_number=queue_row,
        )

    def build_queues(self, queues: list[ImportedSheetsRow]) -> list[Queue]:
        created_queues = []
        for queue in queues:
            created_queues.append(self.build_queue(queue))
        return created_queues
