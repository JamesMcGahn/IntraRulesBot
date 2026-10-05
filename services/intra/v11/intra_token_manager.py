from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
from ..models.token_data import TokenData

import time

import jwt
from PySide6.QtCore import QTimer, Signal, Slot

from base import QObjectBase


class IntraTokenManager(QObjectBase):
    token_status = Signal(str)
    schedule_requested = Signal(str)
    request_refresh = Signal(object)

    def __init__(self, session: IntraProviderSession, logger: LogAdapter):
        super().__init__(logger)
        self.session = session
        self.token_fetch_in_progress = False
        self.token_tries = 0
        self.token_threads = {}

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self.refresh_token)
        self.REFRESH_BUFFER = 30
        self._tenant = None
        self.schedule_requested.connect(self._schedule_token)

    @property
    def tenant(self) -> str:
        return self._tenant

    @tenant.setter
    def tenant(self, tenant: str) -> None:
        self._tenant = tenant

    def remove_bearer(self, token):
        if token is None:
            return None
        return token.split("Bearer ")[1] if token.startswith("Bearer ") else token

    def is_token_usable(self, token) -> bool:
        if token is None or self._tenant is None:
            return False
        time_left = self.token_time_left(token)
        return time_left > self.REFRESH_BUFFER

    def token_time_left(self, token) -> int:
        if token is None:
            return 0
        decoded = jwt.decode(token, options={"verify_signature": False})
        expire_timestamp = decoded.get("exp")
        now_timestamp = int(time.time())
        return expire_timestamp - now_timestamp

    def check_token(self, token) -> bool:
        try:
            token = self.remove_bearer(token)
            valid = self.is_token_usable(token)

            if not valid:
                self._logging(
                    "Session token going to expire. Trying to get a new token"
                )
                return False
            else:
                self.schedule_token(token)
                return True

        except Exception as e:
            self._logging(f"{e}", "ERROR")
            self._logging("Error decoding Session token.", "ERROR")
            return False

    def schedule_token(self, token):
        self.schedule_requested.emit(token)

    @Slot(str)
    def _schedule_token(self, token):
        try:
            token = self.remove_bearer(token)
            time_left = self.token_time_left(token)
            refresh_in = max(time_left - self.REFRESH_BUFFER, 0)

            self._logging(f"Intra token is still valid for {time_left} seconds.")
            self.refresh_timer.stop()  # cancel previous timer
            self.refresh_timer.start(refresh_in * 1000)
            self._logging(f"Scheduling a new token request in {refresh_in} seconds.")
            return True
        except Exception as e:
            self._logging(f"Error scheduling token. {e}")
            return False

    def refresh_token(self):
        if self.token_fetch_in_progress:
            return

        if self.token_tries >= 3:
            return

        self.token_fetch_in_progress = True
        token_data = TokenData(
            self.tenant, self.session.refresh_token, self.session.access_token
        )
        self.request_refresh.emit(token_data)
        self._logging("Sent Token Refresh Request Signal", "DEBUG")
        self.token_tries += 1

    @Slot(object)
    def receive_token(self, token: TokenData):
        self._clear_fetch_flag()

        if self.check_token(token.access_token):
            self._logging("Token was Recieved.")
            self.session.access_token = token.access_token
            self.session.refresh_token = token.refresh_token
            self.token_tries = 0

    @Slot()
    def token_failed(self):
        self._clear_fetch_flag()
        self._logging("Failed to Receive Token.", "ERROR")
        self.session.access_token = None
        self.session.refresh_token = None
        if self.token_tries < 3:
            wait_time = self.token_tries * 30000
            self._logging(
                f"Waiting {int(wait_time/1000)} seconds before reattempting getting token ",
                "INFO",
            )
            QTimer.singleShot(wait_time, self.refresh_token)
        else:
            self._logging(
                "Tried three times to get a token. Failed to get token.",
                "ERROR",
            )

    def _clear_fetch_flag(self):
        self.token_fetch_in_progress = False
