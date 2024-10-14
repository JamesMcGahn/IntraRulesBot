from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..utils import WaitConditions, WebElementInteractions


class TriggerWorker(QWorkerBase):
    """
    Worker class responsible for handling trigger actions within rules, particularly
    setting frequency-based triggers using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        rule (dict): The rule data containing trigger information.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        rule (dict): The rule data containing trigger information.
    """

    def __init__(self, driver: webdriver.Chrome, rule: dict):
        """
        Initializes the TriggerWorker with the provided driver and rule data.
        Sets up the necessary connections for interacting with web elements.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data containing trigger information.
        """
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    @ErrorWrappers.qworker_web_raise_error
    def do_work(self) -> None:
        """
        Executes the trigger action by checking if the rule is frequency-based.
        If it is, sets the frequency-based trigger. Emits the finished signal when complete.

        Returns:
            None: This function does not return a value.
        """
        if "frequency_based" in self.rule:
            self.log_thread()
            self.set_frequency_based()
        self.finished.emit()

    def set_frequency_based(self) -> None:
        """
        Sets the frequency-based time interval for the rule.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Setting rule frequency time interval...", "INFO")
        freq_time_dropdown = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
            WaitConditions.VISIBILITY,
            raise_exception=True,
        )
        freq_time_dropdown.click()

        # Set Frequency Rule Time ->>
        user_time_selection = str(self.rule["frequency_based"]["time_interval"])

        time_selection = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
            user_time_selection,
        )
        if not time_selection:

            self.logging(
                f"Unable to select time {user_time_selection}. Check that your time selection is one of '1','5','10','15','30','60'",
                "ERROR",
            )
            raise ValueError

        sleep(1)
