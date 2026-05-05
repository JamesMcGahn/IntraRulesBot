from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rules.models import Rule
    from .interfaces import RuleRunnerConfigProvider
from PySide6.QtCore import Signal, QThread
from base import QObjectBase
from .rule_runner_worker import RuleRunnerWorker


class RuleRunnerService(QObjectBase):
    progress = Signal(int, int)

    def __init__(self, settings_provider: RuleRunnerConfigProvider):
        super().__init__()
        self._thread = None
        self._worker = None
        self._settings_provider = settings_provider

    def start_run(self, rules: list[Rule]):
        if self._thread and self._thread.isRunning():
            return

        login_config = self._settings_provider.get_rule_run_config()

        self._thread = QThread()
        self._worker = RuleRunnerWorker(rules, login_config)

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.do_work)
        self._worker.done.connect(self._thread.quit)
        self._worker.done.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def stop_run(self):
        if self._worker:
            pass
            # send signal
