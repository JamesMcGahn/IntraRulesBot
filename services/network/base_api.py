from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.network_request import NetworkRequest
    from .models.network_response import NetworkResponse
    from services.logger.adapters import LogAdapter

from base import QObjectBase
from .network_client import NetworkClient
from PySide6.QtCore import Signal


class BaseApi(QObjectBase):
    """Base case for Api"""

    done = Signal()

    def __init__(self, logger: LogAdapter, network_client: NetworkClient):
        super().__init__(logger)
        self._client = network_client

    def _execute(self, request: NetworkRequest) -> NetworkResponse:
        return self._client.execute(request)
