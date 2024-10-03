# from rule_runner_worker import RuleRunnerWorker
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from managers import WebDriverManager

from .login import LoginManagerWorker
from .rule_worker import RuleWorker
from .utils import WebElementInteractions


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
        self.rules = deque()
        for rule in rules:
            self.rules.append(rule)

        self.driver_manager = WebDriverManager()
        self.driver = self.driver_manager.get_driver()
        self.wELI = WebElementInteractions(self.driver)
        self.executor = ThreadPoolExecutor(max_workers=8)
        self._rule_finished = False
        self.current_rule = None
        self.errors_in_a_row = 0
        self.errored_rules = []
        self.success_rules = []

    def run(self):
        self.receiver_thread_logs(
            f"Starting RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
        self.get_login_url()
        self.start_login()

    def get_login_url(self):
        self.driver.get(self.url)

    def start_login(self):
        self.login_worker = LoginManagerWorker(
            self.driver,
            self.username,
            self.password,
            self.url,
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
            self.receiver_thread_logs(
                "Login Failed due to an error. Shutting down thread", "ERROR"
            )
            self.process_finished_()
            self.close()

    def process_next_rule(self):
        print("lennnnnnnn", len(self.rules))
        if len(self.rules) > 0:
            print("erereere33333")
            try:
                self.pause_if_needed(self._paused)
                self.current_rule = self.rules.popleft()
                rule_worker = RuleWorker(self.driver, self.current_rule)
                rule_worker.send_logs.connect(self.receiver_thread_logs)
                rule_worker.error.connect(self.on_rule_error)
                rule_worker.error.connect(rule_worker.deleteLater)
                rule_worker.finished.connect(self.on_rule_finished)
                rule_worker.finished.connect(rule_worker.deleteLater)
                self.executor.submit(rule_worker.do_work)
            except Exception as e:
                self.receiver_thread_logs(
                    f"Failure trying to process next rule: {e}", "ERROR"
                )

        else:
            print("shut down")
            # TODO: Add logging for error rule flow
            for rule in self.errored_rules:
                print("errored", rule["rule_name"])
            for rule in self.success_rules:
                print("success", rule["rule_name"])
            self.executor.shutdown()
            self.process_finished_()

    def on_rule_error(self):
        self.errors_in_a_row += 1
        print("received error from rule worker")
        print("error_in_a_row", self.errors_in_a_row)
        if self.errors_in_a_row < 2:
            print("less than two")
            print("trying next rule")
            self.rules.appendleft(self.current_rule)
            self.get_login_url()
            self.start_login()

        else:
            print("appending")
            self.errored_rules.append(self.current_rule)
            print("next rule")
            self.get_login_url()
            self.start_login()

    def process_finished_(self):
        self.driver_manager.close()
        self.finished.emit()

    @Slot()
    def on_rule_finished(self):
        self.receiver_thread_logs("RuleWorker finished.", "INFO")
        self.success_rules.append(self.current_rule)
        self.errors_in_a_row = 0
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

    @Slot(bool)
    def close(self):
        """
        Close the  properly.
        """
        self.receiver_thread_logs(
            f"Shutting down RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )

        self.process_finished_()
        self.stop()
        self.quit()
        self.wait()
