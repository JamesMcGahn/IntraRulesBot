from time import sleep

from selenium.webdriver.common.by import By

from ..utils import WaitConditions, WebElementInteractions, WorkerClass


class TriggerWorker(WorkerClass):
    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    def do_work(self):
        try:
            if "frequency_based" in self.rule:
                self.log_thread()
                self.set_frequency_based()
        except Exception as e:
            self.logging(f"Something went wrong in TriggerWorker: {e}", "ERROR")
            raise Exception(e) from Exception

    def set_frequency_based(self):
        self.logging("Setting rule frequency time interval...", "INFO")
        freq_time_dropdown = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
            WaitConditions.VISIBILITY,
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
            print(
                f"Unable to select time {user_time_selection}. Check that your time selection is one of '1','5','10','15','30','60'"
            )
            return

        sleep(2)
