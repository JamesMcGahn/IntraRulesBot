from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService
    from ..intra.intra_provider_session import IntraProviderSession
    from ..logger.adapters import LogAdapter
    from ..base.models import JobRequest
    from .models import RuleRunnerRequestPayload
    from ..browser import BrowserSessionFactory
    from ..profiles import ProfileRegistry
from PySide6.QtCore import Signal, QThread, QObject
from .rule_runner_worker import RuleRunnerWorker


class RuleRunnerService(QObject):
    progress = Signal(int, int)
    stop_run = Signal()

    def __init__(
        self,
        session: IntraProviderSession,
        auth_service: AuthService,
        browser_session_factory: BrowserSessionFactory,
        logger: LogAdapter,
        profile_registry: ProfileRegistry,
    ):
        super().__init__()
        self._thread = None
        self._worker = None
        self._session = session
        self._auth_service = auth_service
        self._logger = logger
        self._browser_session_factory = browser_session_factory
        self._profile_registry = profile_registry

    def start_run(self, job: JobRequest[RuleRunnerRequestPayload]) -> None:
        if self._thread and self._thread.isRunning():
            return

        self._thread = QThread()
        self._worker = RuleRunnerWorker(
            job,
            self._browser_session_factory,
            self._session,
            self._auth_service,
            self._logger,
            self._profile_registry,
        )

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.do_work)
        self._worker.done.connect(self._thread.quit)
        self._worker.done.connect(self._worker.deleteLater)
        self._worker.progress.connect(self.progress)
        self._thread.finished.connect(self._clean_up_thread)
        self._thread.start()

    def _clean_up_thread(self):
        if self._thread:
            self._thread.deleteLater()
            self._thread = None
            self._worker = None

    def stop_current_run(self):
        if self._worker:
            self._worker.stop()
