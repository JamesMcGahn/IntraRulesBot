from time import sleep

from PySide6.QtCore import QObject
from selenium.webdriver.common.by import By

from web_element_interactions import WaitConditions, WebElementInteractions


class TriggerWorker(QObject):
    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)

    def do_work(self):
        if "frequency_based" in self.rule:
            self.set_frequency_based()

    def set_frequency_based(self):
        freq_time_dropdown = self.wELI.wait_for_element(
            10,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
            WaitConditions.VISIBILITY,
        )
        freq_time_dropdown.click()

        # Set Frequency Rule Time ->>
        user_time_selection = str(self.rule["frequency_based"]["time_interval"])

        time_selection = self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
            user_time_selection,
        )
        if not time_selection:
            print(
                f"Unable to select time {user_time_selection}. Check that your time selection is one of '1','5','10','15','30','60'"
            )
            return

        sleep(5)
