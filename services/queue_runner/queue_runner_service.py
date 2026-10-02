from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService
    from services.auth.session.session_registry import SessionRegistry
    from ..logger.adapters import LogAdapter
    from ..base.models import JobRequest
    from .models import QueueRunnerRequestPayload
    from ..browser import BrowserSessionFactory
    from ..profiles import ProfileRegistry
    from ..api.queues.queue_v11_api import V11QueueApi

from PySide6.QtCore import QObject, QThread, Signal

from .queue_runner_worker import QueueRunnerWorker


class QueueRunnerService(QObject):
    stop_run = Signal()
    task_progress = Signal(object)
    batch_task_progress = Signal(list)
    progress_status = Signal(int, int)
    runner_life_cyle = Signal(object)
    shutdown_ready = Signal(str)

    def __init__(
        self,
        session: SessionRegistry,
        auth_service: AuthService,
        browser_session_factory: BrowserSessionFactory,
        logger: LogAdapter,
        profile_registry: ProfileRegistry,
        queue_api: V11QueueApi,
    ):
        super().__init__()
        self._thread = None
        self._worker = None
        self._session = session
        self._auth_service = auth_service
        self._logger = logger
        self._browser_session_factory = browser_session_factory
        self._profile_registry = profile_registry
        self._queue_api = queue_api
        self._shut_down_in_requested = False

    def start_run(self, job: JobRequest[QueueRunnerRequestPayload]) -> None:
        if self._thread and self._thread.isRunning():
            return
        session = self._session.current_session()
        self._thread = QThread()
        self._worker = QueueRunnerWorker(
            job,
            self._browser_session_factory,
            session,
            self._auth_service,
            self._logger,
            self._profile_registry,
            self._queue_api,
        )

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.do_work)
        self._worker.runner_life_cyle.connect(self.runner_life_cyle)
        self._worker.done.connect(self._thread.quit)
        self._worker.done.connect(self._worker.deleteLater)
        self._worker.task_progress.connect(self.task_progress)
        self._worker.batch_task_progress.connect(self.batch_task_progress)
        self._worker.progress_status.connect(self.progress_status)
        self._thread.finished.connect(self._clean_up_thread)
        self._thread.start()

    def _clean_up_thread(self):
        if self._thread:
            self._logger(
                f"{self.__class__.__name__}: Queue Runner Thread finished. Cleaning up.",
                "INFO",
            )
            self._thread.deleteLater()
            self._clean_up_refs()

        if self._shut_down_in_requested:
            self._shut_down_in_requested = False
            self.shutdown_ready.emit("queue_runner")

    def _clean_up_refs(self):
        self._worker = None
        self._thread = None

    def request_app_shutdown(self) -> bool:
        if not self._thread or not self._thread.isRunning():
            return True
        self._logger(
            f"{self.__class__.__name__}: Runner still active. Deferring app shutdown.",
            "WARN",
        )
        self._shut_down_in_requested = True
        self.stop_current_run()
        return False

    def stop_current_run(self):
        if self._worker:
            self._worker.stop()
