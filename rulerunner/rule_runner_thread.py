import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal, Slot
from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from managers import WebDriverManager

from .login import LoginManagerWorker
from .rule_worker import RuleWorker
from .utils import WebElementInteractions


class RuleRunnerThread(QThread):
    """
    A thread class responsible for executing a sequence of rules in the application.
    Manages Selenium WebDriver interactions, login process, and rule execution flow with
    support for retries and error handling.

    Attributes:
        username (str): The username for login.
        password (str): The password for login.
        login_url (str): The login URL to access the system.
        url (str): The base URL for accessing the application.
        rules (deque): A deque containing the rules to be processed.
        rules_total_count (int): The total number of rules to process.
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        executor (ThreadPoolExecutor): Thread pool for executing rule workers concurrently.
        current_rule (dict or None): The rule currently being processed.
        errors_in_a_row (int): Tracks the number of consecutive errors encountered.
        errored_rules (list): List of rule names that failed during execution.
        success_rules (list): List of rule names that succeeded during execution.
        login_attempt (bool): Tracks whether a login attempt has been made.
        shut_down (bool): Tracks if the thread is shutting down.

    Signals:
        finished (Signal): Signal emitted when the thread finishes execution.
        send_insert_logs (Signal[str, str, bool]): Signal for sending logs.
        progress (Signal[int, int]): Signal to update rule processing progress.
        rule_created (Signal[str]): Signal emitted when a rule is successfully created.

    Args:
        username (str): The username for login.
        password (str): The password for login.
        login_url (str): The login URL to access the system.
        url (str): The base URL for accessing the application.
        rules (list): List of rules to process.
    """
    finished = Signal()
    send_insert_logs = Signal(str, str, bool)
    progress = Signal(int, int)
    rule_created = Signal(str)

    def __init__(self, username:str, password:str, login_url:str,url:str, rules:list):
        """
        Initializes the RuleRunnerThread with the provided username, password, login URL, and rules.

        Args:
            username (str): The username for login.
            password (str): The password for login.
            login_url (str): The login URL to access the system.
            url (str): The base URL for accessing the application.
            rules (list): List of rules to process.
        """
        super().__init__()

        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False

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
        self.shut_down = False

    def run(self)->None:
        """
        Starts the RuleRunnerThread, initializes the driver, and begins the login process.

        Returns:
            None: This function does not return a value.
        """
        self.receiver_thread_logs(
            f"Starting RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
        self.init_driver()
        self.get_login_url()
        self.start_login()

    def init_driver(self)->None:
        """
        Initializes the Selenium WebDriver through the WebDriverManager.

        Returns:
            None: This function does not return a value.
        """
        self.driver_manager = WebDriverManager()
        self.driver_manager.moveToThread(self)

        self.driver_manager.send_logs.connect(self.receiver_thread_logs)
        self.driver_manager.init_driver()
        self.driver = self.driver_manager.get_driver()

    def close_down_driver(self):
        """
        Closes and cleans up the Selenium WebDriver instance.

        Returns:
            None: This function does not return a value.
        """
        self.driver_manager.close()
        self.driver_manager.deleteLater()

    def get_login_url(self)->None:
        """
        Loads the login URL in the browser. Handles exceptions such as browser closure
        and retries if necessary.

        Returns:
            None: This function does not return a value.
        """
        try:
            self.driver.get(self.login_url)
            self.receiver_thread_logs(f"Loaded in the browser: {self.url} ","INFO"
        )
        except NoSuchWindowException:
            self.receiver_thread_logs("Error loading URL. Browser closed.","ERROR")
            self.receiver_thread_logs("Restarting WebDriver.....","INFO")
            if not self.shut_down:
                self.init_driver()
                self.driver.get(self.login_url)
        except WebDriverException as e:
            if not self.shut_down:
                self.receiver_thread_logs(f"Error loading URL. Browser likely closed: {str(e)}","ERROR")
                self.receiver_thread_logs("Restarting WebDriver.....","INFO")
                self.init_driver()
                self.driver.get(self.login_url)
        except Exception as e:
            self.receiver_thread_logs(f"Error loading URL.: {str(e)}","ERROR")
            self.close()

    def start_login(self)->None:
        """
        Starts the login process by initializing and running the LoginManagerWorker.

        Returns:
            None: This function does not return a value.
        """
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
    def receiver_thread_logs(self, msg:str, level:str, print_msg:bool=True)->None:
        """
        Receives and logs messages from the thread.

        Args:
            msg (str): The log message.
            level (str): The log level (e.g., "INFO", "ERROR").
            print_msg (bool, optional): Whether to print the message.

        Returns:
            None: This function does not return a value.
        """
        if not self.shut_down:
            self.send_insert_logs.emit(msg, level, print_msg)

    @Slot()
    def login_error(self)->None:
        """
        Handles login errors. Retries login if it hasn't been attempted, otherwise shuts down the thread.

        Returns:
            None: This function does not return a value.
        """
        if not self.login_attempt and not self.shut_down:
            self.login_attempt = True
            self.login_worker.deleteLater()
            self.receiver_thread_logs(
                "Login Failed due to an error. Retrying again.", "INFO"
            )
            self.get_login_url()
            self.start_login()
        else:
            self.login_worker.deleteLater()
            if not self.shut_down:
                self.receiver_thread_logs(
                    "Login Failed due to an error. Shutting down thread", "ERROR"
                )
            self.close()

    @Slot()
    def login_success(self)->None:
        """
        Processes the next rule after a successful login.

        Returns:
            None: This function does not return a value.
        """
        self.process_next_rule()
        self.login_worker.deleteLater()

    def process_next_rule(self)->None:
        """
        Processes the next rule in the queue by initializing and running the RuleWorker.

        Returns:
            None: This function does not return a value.
        """
        if self.shut_down:
            return
        rules_length = len(self.rules)
        self.progress.emit(self.rules_total_count - rules_length, self.rules_total_count)
        if rules_length > 0:
            try:
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

    def create_rule_summary(self)->None:
        """
        Creates a summary of successfully executed and errored rules.

        Returns:
            None: This function does not return a value.
        """
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
    def on_rule_error(self, shouldRetry:bool)->None:
        """
        Handles rule processing errors and decides whether to retry or skip the rule.

        Args:
            shouldRetry (bool): Indicates whether to retry the rule.

        Returns:
            None: This function does not return a value.
        """
        self.errors_in_a_row += 1
        self.receiver_thread_logs("RuleRunnerThread received error from Rule Worker.", "WARN")
        self.receiver_thread_logs(f"Rule: {self.current_rule["rule_name"]} has errored out {self.errors_in_a_row} times.", "WARN")
        if self.errors_in_a_row < 2 and shouldRetry and not self.shut_down:
            self.receiver_thread_logs(f"Trying Again to create Rule for {self.current_rule["rule_name"]}", "INFO")
            self.rules.appendleft(self.current_rule)
            self.get_login_url()
            self.start_login()
        else:
            msg = f"Skipping Rule due to {self.errors_in_a_row} errors in a row" if shouldRetry else "Skipping Rule - "
            if not self.shut_down:

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
    def on_rule_finished(self, rule_name:str)->None:
        """
        Handles the completion of a rule and proceeds to process the next one.

        Args:
            rule_name (str): The name of the rule that was successfully created.

        Returns:
            None: This function does not return a value.
        """
        self.receiver_thread_logs("RuleWorker finished.", "INFO")
        self.success_rules.append(rule_name)
        self.rule_created.emit(rule_name)
        self.errors_in_a_row = 0
        self.process_next_rule()


    @Slot()
    def stop(self)->None:
        """
        Stops the thread execution.

        Returns:
            None: This function does not return a value.
        """
        self.close()

    def is_thread_pool_running(self)->bool:
        """
        Checks if the thread pool is still running any threads.

        Returns:
            bool: True if the thread pool is running, False otherwise.
        """
        return any(thread.is_alive() for thread in self.executor._threads)


    @Slot(bool)
    def close(self)->None:
        """
        Closes the thread and ensures proper shutdown of all resources.

        Returns:
            None: This function does not return a value.
        """
        if self.isRunning() or self.is_thread_pool_running():
            self.receiver_thread_logs(
                f"Shutting down RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
                "INFO",
            )
            self.shut_down = True
            self.close_down_driver()
            if self.is_thread_pool_running():
                self.executor.shutdown(wait=False,cancel_futures=True)
            
            self.finished.emit()
            self.wait()
            self.quit()
            self.deleteLater()