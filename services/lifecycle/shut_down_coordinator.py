from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocols import ShutdownAware
    from ..logger.adapters import LogAdapter

from PySide6.QtCore import Signal, QObject


class ShutdownCoordinator(QObject):
    shutdown_confirmed = Signal()

    def __init__(self, logger: LogAdapter):
        super().__init__()
        self.logger = logger
        self._services: dict[str, ShutdownAware] = {}
        self._pending: set[str] = set()
        self._shutdown_started = False

    def register_service(self, service_name: str, service: ShutdownAware) -> None:
        self._services[service_name] = service
        service.shutdown_ready.connect(
            lambda service_name: self._on_service_ready(service_name)
        )

    def request_shutdown(self) -> bool:
        if self._shutdown_started:
            return False

        self._shutdown_started = True
        self._pending.clear()

        for service_name, service in self._services.items():
            ready_for_shutdown = service.request_app_shutdown()

            if not ready_for_shutdown:
                self._pending.add(service_name)

        if self._pending:
            self.logger(
                f"{self.__class__.__name__}: Defering Shutdown. Waiting on services: {self._pending}",
                "WARN",
            )
            return False

        self._clear_to_shut_down()
        return True

    def _on_service_ready(self, service_name: str) -> None:
        if not self._shutdown_started:
            return

        self._pending.discard(service_name)

        if not self._pending:
            self._clear_to_shut_down()

    def _clear_to_shut_down(self):
        self.logger(
            f"{self.__class__.__name__}: No Threaded Services Running. Clear for Shutdown.",
            "INFO",
        )
        self.shutdown_confirmed.emit()
