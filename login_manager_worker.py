import threading

from PySide6.QtCore import QObject, Signal
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from services.logger import Logger
from web_element_interactions import WaitConditions, WebElementInteractions


class LoginManagerWorker(QObject):
    status_signal = Signal(bool)
    send_logs = Signal(str, str, bool)

    def __init__(self, driver, username, password, url):
        super().__init__()
        self.driver = driver
        self.url = url
        self.username = username
        self.password = password
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    def logging(self, msg, level, print_msg=True):
        self.send_logs.emit(msg, level, print_msg)

    def do_work(self):
        try:
            self.logging(
                f"Starting LoginManagerWorker in thread: {threading.get_ident()} - {self.thread()}",
                "INFO",
            )

            self.enter_login_info()
            self.wait_for_session_alert()
            self.wait_for_success()
        except Exception as e:
            self.logging(f"Exception in LoginManagerWorker: {str(e)}", "ERROR")
            self.status_signal.emit(False)

    def enter_login_info(self):
        login_name_field = self.driver.find_element(By.ID, "inputUserName")
        login_name_field.send_keys(self.username)

        login_pw_field = self.driver.find_element(By.ID, "inputPassword")
        login_pw_field.send_keys(self.password)

        login_btn = self.driver.find_element(By.ID, "btnLogin")
        login_btn.click()

    def wait_for_session_alert(self):
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            alert.accept()
            print("herer")
            self.logging(
                "Session open elsewhere alert was present. Accepted alert to proceed with this session.",
                "INFO",
            )

        except TimeoutException:
            print()
            self.logging("No session alert was present.", "INFO")
        except Exception as e:
            print(e)
            self.logging(e.message, "ERROR")

        return

    def wait_for_success(self):
        error_login = self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[@id="loginErrorContainer"]/span',
            WaitConditions.VISIBILITY,
            failure_message=("INFO", "Login successful."),
        )

        if error_login:
            self.logging(f"Error during login: {error_login.text}", "ERROR")

            self.status_signal.emit(False)
        else:
            self.move_to_rules_page()

    def move_to_rules_page(self):

        if self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[contains(@id, "radTabStripSubNavigation")]',
            WaitConditions.PRESENCE,
        ):
            self.logging("Navigating to the Rules Page...", "INFO")
            self.driver.get(self.url + "/ManagerConsole/Delivery/Rules.aspx")

            self.status_signal.emit(True)
        else:
            self.status_signal.emit(False)
        self.logging("Ending Login Worker Thread...", "INFO")
