from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from services.network.network_client import NetworkClient
    from services.network.models import NetworkResponse
    from requests import Response

from PySide6.QtCore import Slot, Signal
from services.network.base_api import BaseApi
from services.network.models import NetworkRequest
from services.network.enums import HTTPMETHOD

from ..models.token_data import TokenData


class IntraTokenApi(BaseApi):
    token_failed = Signal()
    token_response = Signal(object)

    def __init__(
        self,
        logger: LogAdapter,
        network_client: NetworkClient,
    ):
        super().__init__(logger, network_client)

    @Slot(object)
    def refesh_token(self, token_data: TokenData) -> NetworkResponse:
        request = NetworkRequest(
            method=HTTPMETHOD.POST,
            url=f"https://{token_data.tenant}auth.intradiem.com/auth/realms/{token_data.tenant}/protocol/openid-connect/token",
            json={
                "grant_type": "refresh_token",
                "refresh_token": token_data.refresh_token,
                "client_id": "intradiem_frontend",
            },
        )

        response = self._execute(request)
        self._logging(f"Received token response: {response}", "DEBUG")
        if not response.ok:
            self._send_failure()
            return
        access_token = response.get("access_token")
        refesh_token = response.get("refresh_token")

        if access_token is None or refesh_token is None:
            self._send_failure(response)

        self.token_response.emit(
            TokenData(
                tenant=token_data.tenant,
                refresh_token=refesh_token,
                access_token=access_token,
            )
        )
        self.done.emit()

    def _send_failure(self, response: Response):
        self._logging(f"Token request failed. status: {response.status_code}")
        self.token_failed.emit()
        self.done.emit()
