# from rule_runner_worker import RuleRunnerWorker
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot
from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from managers import WebDriverManager

from .login import LoginManagerWorker
from .rule_worker import RuleWorker
from .utils import WebElementInteractions


class RuleRunnerThread(QThread):
    finished = Signal()
    send_insert_logs = Signal(str, str, bool)
    progress = Signal(int, int)
    rule_created = Signal(str)

    def __init__(self, username, password, login_url,url, rules):
        super().__init__()

        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

        self.username = username
        self.password = password
        self.url = url
        self.login_url = login_url
        self.rules = deque()
        self.rules_total_count = len(rules)
        for rule in rules:
            self.rules.append(rule)

        self.driver = None
        self.wELI = WebElementInteractions(self.driver)
        self.executor = ThreadPoolExecutor(max_workers=8)
        self._rule_finished = False
        self.current_rule = None
        self.errors_in_a_row = 0
        self.errored_rules = []
        self.success_rules = []
        self.login_attempt = False

    def run(self):
        self.receiver_thread_logs(
            f"Starting RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
        self.init_driver()
        self.get_login_url()
        self.start_login()

    def init_driver(self):
        self.driver_manager = WebDriverManager()
        self.driver_manager.moveToThread(self)

        self.driver_manager.send_logs.connect(self.receiver_thread_logs)
        self.driver_manager.init_driver()
        self.driver = self.driver_manager.get_driver()

    def close_down_driver(self):
        self.driver_manager.close()
        self.driver_manager.deleteLater()

    def get_login_url(self):
        try:
            self.driver.get(self.login_url)
            self.receiver_thread_logs(f"Loaded in the browser: {self.url} ","INFO"
        )
        except NoSuchWindowException:
            self.receiver_thread_logs("Error loading URL. Browser closed.","ERROR")
            self.receiver_thread_logs("Restarting WebDriver.....","INFO")
            self.init_driver()
            self.driver.get(self.login_url)
        except WebDriverException as e:
            self.receiver_thread_logs(f"Error loading URL. Browser likely closed: {str(e)}","ERROR")
            self.receiver_thread_logs("Restarting WebDriver.....","INFO")
            self.init_driver()
            self.driver.get(self.login_url)
        except Exception as e:
            self.receiver_thread_logs(f"Error loading URL.: {str(e)}","ERROR")
            self.close()

    def start_login(self):
        self.login_worker = LoginManagerWorker(
            self.driver,
            self.username,
            self.password,
            self.url,
        )
        self.login_worker.moveToThread(self)
        self.login_worker.send_logs.connect(self.receiver_thread_logs)
        self.login_worker.error.connect(self.login_error)
        self.login_worker.finished.connect(self.login_success)
        self.login_worker.do_work()

    @Slot(str, str, bool)
    def receiver_thread_logs(self, msg, level, print_msg=True):
        self.send_insert_logs.emit(msg, level, print_msg)

    @Slot()
    def login_error(self):
        if not self.login_attempt:
            self.login_attempt = True
            self.login_worker.deleteLater()
            self.receiver_thread_logs(
                "Login Failed due to an error. Retrying again.", "INFO"
            )
            self.get_login_url()
            self.start_login()
        else:
            self.login_worker.deleteLater()
            self.receiver_thread_logs(
                "Login Failed due to an error. Shutting down thread", "ERROR"
            )
            self.close()

    @Slot()
    def login_success(self):
        self.process_next_rule()
        self.login_worker.deleteLater()

    def process_next_rule(self):
        rules_length = len(self.rules)
        self.progress.emit(self.rules_total_count - rules_length, self.rules_total_count)
        if rules_length > 0:
            try:
                with QMutexLocker(self._mutex):
                    if self._paused:
                        self._wait_condition.wait(self._mutex)
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
                    f"Failure trying to process next rule: {e}",
                    "ERROR",
                )

        else:
            self.create_rule_summary()
            self.close()

    def create_rule_summary(self):
            errored_rules_msg = f'ERRORED RULES TOTAL: {len(self.errored_rules)} \n'
            succeeded_rules_msg = f'SUCCEEDED RULES TOTAL: {len(self.success_rules)} \n'
            tabs = '\t' * 4
            for e_rule_name in self.errored_rules:
                errored_rules_msg += f'{tabs}- {e_rule_name} \n'
            for s_rule_rume in self.success_rules:
                succeeded_rules_msg += f'{tabs}- {s_rule_rume} \n'
            self.receiver_thread_logs(succeeded_rules_msg, "INFO")
            self.receiver_thread_logs(errored_rules_msg, "ERROR")


    @Slot(bool)
    def on_rule_error(self, shouldRetry):
        self.errors_in_a_row += 1
        self.receiver_thread_logs("RuleRunnerThread received error from Rule Worker.", "WARN")
        self.receiver_thread_logs(f"Rule: {self.current_rule["rule_name"]} has errored out {self.errors_in_a_row} times.", "WARN")
        if self.errors_in_a_row < 2 and shouldRetry:
            self.receiver_thread_logs(f"Trying Again to create Rule for {self.current_rule["rule_name"]}", "INFO")
            self.rules.appendleft(self.current_rule)
            self.get_login_url()
            self.start_login()
        else:
            msg = f"Skipping Rule due to {self.errors_in_a_row} errors in a row" if shouldRetry else "Skipping Rule - "

            self.receiver_thread_logs(msg, "INFO")
            self.errored_rules.append(self.current_rule["rule_name"])
            if len(self.rules) > 0:
                self.get_login_url()
                self.start_login()
                self.errors_in_a_row = 0
            else:
                self.create_rule_summary()
                self.close()


    @Slot(str)
    def on_rule_finished(self, rule_name):
        self.receiver_thread_logs("RuleWorker finished.", "INFO")
        self.success_rules.append(rule_name)
        self.rule_created.emit(rule_name)
        self.errors_in_a_row = 0
        self.process_next_rule()



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
        self.pause()
        self.close()

    @Slot(bool)
    def close(self):
        """
        Close the  properly.
        """
        if self.isRunning():
            self.receiver_thread_logs(
                f"Shutting down RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
                "INFO",
            )
            self.close_down_driver()
            self.finished.emit()
            self.quit()
            self.wait()