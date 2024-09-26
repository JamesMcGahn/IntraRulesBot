# from rule_runner_worker import RuleRunnerWorker
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from login_manager_worker import LoginManagerWorker
from rule_worker import RuleWorker
from services.logger import Logger
from web_driver_manager import WebDriverManager
from web_element_interactions import WebElementInteractions


class RuleRunnerThread(QThread):
    finished = Signal()
    send_insert_logs = Signal(str, str, bool)

    def __init__(self, username, password, url, rules):
        super().__init__()

        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

        self.username = username
        self.password = password
        self.url = url
        self.rules = Queue()
        for rule in rules:
            self.rules.put(rule)
        self.driver_manager = WebDriverManager()
        self.driver = self.driver_manager.get_driver()
        self.wELI = WebElementInteractions(self.driver)
        self.executor = ThreadPoolExecutor(max_workers=8)
        self._rule_finished = False

    def run(self):
        self.receiver_thread_logs(
            f"Starting RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
        self.driver.get(self.url)
        self.login_worker = LoginManagerWorker(
            self.driver, self.username, self.password, self.url
        )
        self.login_worker.status_signal.connect(self.login_responses)
        self.login_worker.send_logs.connect(self.receiver_thread_logs)
        self.login_worker.moveToThread(self)
        self.login_worker.do_work()

    @Slot(str, str, bool)
    def receiver_thread_logs(self, msg, level, print_msg=True):
        self.send_insert_logs.emit(msg, level, print_msg)

    @Slot(bool)
    def login_responses(self, status):
        if status:
            self.process_next_rule()
            self.login_worker.deleteLater()
        else:
            self.login_worker.deleteLater()

    def process_next_rule(self):
        if not self.rules.empty():
            self.pause_if_needed(self._paused)
            rule = self.rules.get()
            rule_worker = RuleWorker(self.driver, rule)
            rule_worker.finished.connect(self.on_rule_finished)
            rule_worker.send_logs.connect(self.receiver_thread_logs)
            rule_worker.finished.connect(self.process_next_rule)
            rule_worker.finished.connect(rule_worker.deleteLater)
            self.executor.submit(rule_worker.do_work)

        else:
            self.finished.emit()
            self.driver_manager.close()
            self.executor.shutdown()

    @Slot()
    def on_rule_finished(self):
        print("RuleWorker finished.")
        self.process_next_rule()

    def wait_for_rule_to_finish(self):
        with QMutexLocker(self._mutex):
            self._rule_finished = False  # Reset for the next rule
            while not self._rule_finished:
                self._wait_condition.wait(self._mutex)

    def pause_if_needed(self, checkVar):
        with QMutexLocker(self._mutex):
            if checkVar:
                self._paused = True

            while self._paused:
                self._wait_condition.wait(self._mutex)

    @Slot()
    def resume(self):
        with QMutexLocker(self._mutex):
            self._paused = False
            self._wait_condition.wakeOne()

    @Slot()
    def pause(self):
        with QMutexLocker(self._mutex):
            self._paused = True

    @Slot()
    def stop(self):
        """Stop the thread."""
        with QMutexLocker(self._mutex):
            self._stop = True
            self._paused = False
            self._wait_condition.wakeAll()
