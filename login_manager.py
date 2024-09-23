from time import sleep

from PySide6.QtCore import QObject, Signal
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from keys import keys
from services.logger import Logger
from web_element_interactions import WaitConditions, WebElementInteractions


class LoginManager(QObject):
    status = Signal(bool)

    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password
        self.wELI = WebElementInteractions(self.driver)

    def login(self):
        super().__init__()
        login_name_field = self.driver.find_element(By.ID, "inputUserName")
        login_name_field.send_keys(self.username)

        login_pw_field = self.driver.find_element(By.ID, "inputPassword")
        login_pw_field.send_keys(self.password)

        login_btn = self.driver.find_element(By.ID, "btnLogin")
        login_btn.click()

        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            alert.accept()
            Logger().insert(
                "Session open elsewhere alert was present. Accepted alert to proceed with this session.",
                "INFO",
            )

        except TimeoutException:
            Logger().insert("INFO", "No session alert was present.")

        error_login = self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[@id="loginErrorContainer"]/span',
            WaitConditions.VISIBILITY,
            failure_message=("INFO", "Login successful."),
        )

        if error_login:
            Logger().insert(f"Error during login: {error_login.text}", "ERROR")

            self.status.emit(False)
        else:

            self.status.emit(True)
