from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.auth.session.session_registry import SessionRegistry
    from .models.network_request import NetworkRequest
    from services.logger.adapters import LogAdapter

from requests import Response, RequestException
from .models.network_response import NetworkResponse
from .enums.auth_mode import AUTHMODE
from base.logging_base import LoggingBase


class NetworkClient(LoggingBase):

    def __init__(self, session_registry: SessionRegistry, logger: LogAdapter):
        super().__init__(logger)
        self._session_registry = session_registry

    def execute(self, request: NetworkRequest):
        provider_session = self._session_registry.current_session()
        session = provider_session.build_session()

        headers = dict(request.headers or {})
        if request.auth_mode == AUTHMODE.BEARER:
            headers["Authorization"] = f"Bearer {provider_session.access_token}"
        self.logging(f"Sending Request to: {request.method} - {request.url}", "INFO")
        try:
            response = session.request(
                method=request.method,
                url=request.url,
                params=request.params,
                headers=headers,
                json=request.json,
                data=request.data,
                files=request.files,
                timeout=request.timeout,
            )

            self._log_response(response)
        except RequestException as e:
            return NetworkResponse(ok=False, status=0, data=None, message=f"{e}")

        provider_session.update_cookies_from_res(response)

        return NetworkResponse(
            ok=True,
            status=response.status_code,
            data=self._extract_payload(response),
            message="success" if response.ok else "error",
        )

    def _log_response(self, response: Response) -> None:
        self.logging(
            f"Response Received: - STATUS: {response.status_code} - METHOD: {response.request.method} - {response.request.url} - Time Elapsed: {response.elapsed}",
            "INFO",
        )
        self.logging(f"Request headers: {response.request.headers}", "DEBUG")
        self.logging(f"Request body: {response.request.body}", "DEBUG")
        self.logging(f"Response headers: {response.headers}", "DEBUG")
        self.logging(f"Response body: {response.text}", "DEBUG")

    @staticmethod
    def _extract_payload(response: Response) -> Any:
        content_type = response.headers.get("Content-Type", "").lower()
        if "json" in content_type:
            try:
                return response.json()
            except ValueError:
                pass
        return response.text
