from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base import QWorkerBase

from ..utils import WaitConditions, WebElementInteractions


class LoginManagerWorker(QWorkerBase):
    """
    Worker class responsible for handling the login process.
    It interacts with the login page, enters credentials, handles session alerts,
    and navigates to the rules page using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        username (str): The username for login.
        password (str): The password for login.
        url (str): The base URL for navigating to the rules page.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        username (str): The username for login.
        password (str): The password for login.
        url (str): The base URL for navigating to the rules page.
    """

    def __init__(
        self, driver: webdriver.Chrome, username: str, password: str, url: str
    ):
        """
        Initializes the LoginManagerWorker with the provided driver, username, password, and URL.
        Sets up the necessary connections for interacting with web elements.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            username (str): The username for login.
            password (str): The password for login.
            url (str): The base URL for navigating to the rules page.
        """
        super().__init__()
        self.driver = driver
        self.url = url
        self.username = username
        self.password = password
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    def do_work(self) -> None:
        """
        Executes the login process by entering login information, handling session alerts,
        waiting for login success, and navigating to the rules page. Emits the error signal
        if any exceptions occur.

        Returns:
            None: This function does not return a value.
        """
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

    def enter_login_info(self) -> None:
        """
        Enters the username and password into the login fields and clicks the login button.

        Returns:
            None: This function does not return a value.
        """
        login_name_field = self.driver.find_element(By.ID, "inputUserName")
        login_name_field.send_keys(self.username)

        login_pw_field = self.driver.find_element(By.ID, "inputPassword")
        login_pw_field.send_keys(self.password)

        login_btn = self.driver.find_element(By.ID, "btnLogin")
        login_btn.click()

    def wait_for_session_alert(self) -> None:
        """
        Waits for a session alert indicating that a session is open elsewhere, and accepts the alert if present.

        Returns:
            None: This function does not return a value.
        """
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

    def wait_for_success(self) -> None:
        """
        Waits for the login success by checking for any error messages. If no error is found, proceeds
        to navigate to the rules page.

        Returns:
            None: This function does not return a value.
        """
        error_login = self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[@id="loginErrorContainer"]/span',
            WaitConditions.VISIBILITY,
            failure_message=("INFO", "Login successful."),
            retries=1,
        )

        if error_login:
            self.logging(f"Error during login: {error_login.text}", "ERROR")

            self.error.emit()
        else:
            self.move_to_rules_page()

    def move_to_rules_page(self) -> None:
        """
        Navigates to the rules page if the login is successful, and emits the finished signal.

        Returns:
            None: This function does not return a value.
        """

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
