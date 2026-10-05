from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from .intra_token_api import IntraTokenApi

from base import QObjectBase
from PySide6.QtCore import Slot, Signal, QThread


class IntraTokenService(QObjectBase):
    token_failed = Signal()
    token_response = Signal(object)
    shutdown_ready = Signal(str)
    request_stop = Signal()
    request_refresh = Signal(object)

    def __init__(self, logger: LogAdapter, token_api: IntraTokenApi):
        super().__init__(logger)
        self._token_worker = token_api
        self._token_thread = None

    @Slot()
    def start_service(self):
        if self._token_thread and self._token_thread.isRunning():
            return
        self._logging(
            f"{self.__class__.__name__}: IntraToken Starting...",
            "INFO",
        )
        self._token_thread = QThread()
        self._token_worker.moveToThread(self._token_thread)
        self._token_worker.token_failed.connect(self.token_failed)
        self._token_worker.token_response.connect(self.token_response)
        self.request_stop.connect(self._token_worker.request_stop)
        self._token_worker.done.connect(self._token_worker.deleteLater)
        self._token_worker.done.connect(self._token_thread.quit)
        self.request_refresh.connect(self._token_worker.refesh_token)
        self._token_thread.finished.connect(self._clean_up_thread)
        self._token_thread.start()

    def request_refreshes(self, token_data):
        self.request_refresh.emit(token_data)

    def _clean_up_thread(self):
        if self._token_thread:
            self._logging(
                f"{self.__class__.__name__}: IntraToken Thread finished. Cleaning up.",
                "INFO",
            )
            self._token_thread.deleteLater()
            self._clean_up_refs()

        if self._shut_down_in_requested:
            self._shut_down_in_requested = False
            self.shutdown_ready.emit("intra_token")

    def _clean_up_refs(self):
        self._token_worker = None
        self._token_thread = None

    def request_app_shutdown(self) -> bool:
        if not self._token_thread or not self._token_thread.isRunning():
            return True
        self._logging(
            f"{self.__class__.__name__}: IntraToken still active. Deferring app shutdown.",
            "WARN",
        )
        self._shut_down_in_requested = True
        self.stop_current_run()
        return False

    def stop_current_run(self):
        if self._token_worker:
            self.request_stop.emit()
