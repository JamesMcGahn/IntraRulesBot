from PySide6.QtCore import Signal
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base import QWorkerBase

from ..utils import WaitConditions, WebElementInteractions


class LoginManagerWorker(QWorkerBase):
    status_signal = Signal(bool)

    def __init__(self, driver, username, password, url):
        super().__init__()
        self.driver = driver
        self.url = url
        self.username = username
        self.password = password
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    def do_work(self):
        try:
            self.log_thread()
            self.enter_login_info()
            self.wait_for_session_alert()
            self.wait_for_success()
        except NoSuchWindowException:
            self.logging(
                "Exception in LoginManagerWorker: the browser was closed", "ERROR"
            )
            self.error.emit()
        except Exception as e:

            self.logging(f"Exception in LoginManagerWorker: {str(e)}", "ERROR")
            self.error.emit()

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
            self.logging(
                "Session open elsewhere alert was present. Accepted alert to proceed with this session.",
                "INFO",
            )

        except TimeoutException:
            self.logging("No session alert was present.", "INFO")

    def wait_for_success(self):
        error_login = self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[@id="loginErrorContainer"]/span',
            WaitConditions.VISIBILITY,
            failure_message=("INFO", "Login successful."),
            retries=0,
        )

        if error_login:
            self.logging(f"Error during login: {error_login.text}", "ERROR")

            self.error.emit()
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

            self.finished.emit()
        else:
            self.logging("Failed to load the Rules Page", "ERROR")
            self.error.emit()
        self.logging("Ending Login Worker Thread...", "INFO")
