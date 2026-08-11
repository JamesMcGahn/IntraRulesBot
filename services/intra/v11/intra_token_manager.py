from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
    from base import ThreadCleanUpManager
    from .intra_token_api import IntraTokenApi

import time

import jwt
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, ThreadCleanUpManager
from base.enums import AUTHVALIDATIONSTATUS


class IntraTokenManager(QObjectBase):
    token_status = Signal(str)

    def __init__(
        self,
        session: IntraProviderSession,
        logger: LogAdapter,
        token_api: IntraTokenApi,
        thread_cleanup_manager: ThreadCleanUpManager,
    ):
        super().__init__(logger)
        self.session = session
        self.cleanup_manager = thread_cleanup_manager
        self.token_api = token_api
        self.token_fetch_in_progress = False
        self.token_tries = 0
        self.token_threads = {}

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self.refresh_token)
        self.REFRESH_BUFFER = 30
        self._tenant = None

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
                self.logging("Session token going to expire. Trying to get a new token")
                return False
            else:
                self.schedule_token(token)
                return True

        except Exception as e:
            self.logging(f"{e}", "ERROR")
            self.logging(
                "Error decoding Session token. Trying to get a new token.",
                "ERROR",
            )
            self.token_status.emit(AUTHVALIDATIONSTATUS.FAILED)
            return False

    def schedule_token(self, token):
        try:
            token = self.remove_bearer(token)
            time_left = self.token_time_left(token)
            refresh_in = max(time_left - self.REFRESH_BUFFER, 0)

            self.logging(f"Intra token is still valid for {time_left} seconds.")
            self.refresh_timer.stop()  # cancel previous timer
            self.refresh_timer.start(refresh_in * 1000)
            self.logging(f"Scheduling a new token request in {refresh_in} seconds.")
            return True
        except Exception as e:
            self.logging(f"Error scheduling token. {e}")
            return False

    def refresh_token(self):
        if self.token_fetch_in_progress:
            return

        if self.token_tries == 3:
            self.logging(
                "Tried three times to get a token. Failed to get token.",
                "ERROR",
            )
            self.token_status.emit(AUTHVALIDATIONSTATUS.FAILED)
            return
        self.token_fetch_in_progress = True
        self.token_status.emit(AUTHVALIDATIONSTATUS.BUSY)
        task_id = f"token_fetch_{self.token_tries}"
        token_thread = QThread()
        token_worker = TokenWorker(session=self.session)
        token_worker.moveToThread(token_thread)
        token_worker.send_token.connect(self.receive_token)
        token_worker.done.connect(
            lambda: self.cleanup_manager.cleanup_task(task_id, False)
        )
        token_thread.finished.connect(
            lambda: self.cleanup_manager.cleanup_task(task_id, True)
        )
        token_thread.started.connect(token_worker.run)
        token_thread.start()
        self.cleanup_manager.add_task(task_id, token_thread, token_worker)
        self.token_tries += 1

    @Slot(str, bool)
    def receive_token(self, token, wasReceived):
        self._clear_fetch_flag()

        if wasReceived and self.check_token(token):
            self.logging("Token was Recieved.")
            self.session.token = token
            self.token_tries = 0
            self.token_status.emit(AUTHVALIDATIONSTATUS.VALID)
        else:
            self.logging("Failed to Receive Token.", "ERROR")
            self.session.token = None
            if self.token_tries < 3:
                wait_time = self.token_tries * 30000
                self.logging(
                    f"Waiting {int(wait_time/1000)} seconds before reattempting getting token ",
                    "INFO",
                )
            else:
                wait_time = 0
            QTimer.singleShot(wait_time, self.refresh_token)

    def _clear_fetch_flag(self):
        self.token_fetch_in_progress = False
