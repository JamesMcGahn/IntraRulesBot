from time import sleep

from selenium.webdriver.common.by import By

from base import QWorkerBase

from ..utils import WaitConditions, WebElementInteractions


class ActionsEmailWorker(QWorkerBase):
    def __init__(self, driver, actions_worker, action, rule, index):
        super().__init__()
        self.driver = driver
        self.action = action
        self.rule = rule
        self.index = index
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = actions_worker.rule_condition_queues_source
        self.wELI.send_msg.connect(self.logging)

    def do_work(self):
        try:
            self.log_thread()
            self.click_email_settings_page()
            self.set_email_subject(self.rule["rule_name"])
            self.set_email_message(self.action)
            self.click_next_page()
            self.set_email_address(self.action)
            self.finished.emit()
        except Exception as e:
            self.logging(f"Something went wrong in ActionsEmailWorker: {e}", "ERROR")
            raise Exception(e) from Exception

    def click_email_settings_page(self):

        email_page_settings_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_lblSettings")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        email_page_settings_btn.click()

    def set_email_subject(self, rule_name):
        self.logging(f"Setting email subject for Action {self.index+1}...", "INFO")
        email_subject = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_ctl05")]',
            WaitConditions.VISIBILITY,
            raise_exception=True,
        )
        email_subject.send_keys(rule_name)

    def set_email_message(self, action):
        self.logging(f"Setting email message for Action {self.index+1}...", "INFO")
        sleep(2)
        print("here")
        if "frequency_based" in self.rule:
            email_message = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )
        else:
            email_message = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl13")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )

        email_message.send_keys(action["details"]["email_body"])
        sleep(2)

    def click_next_page(self):
        continue_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        continue_btn.click()

    def set_email_address(self, action):
        self.logging(
            f"Setting receiver email address for Action {self.index+1}...", "INFO"
        )
        select_email_individual = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        select_email_individual.click()

        if self._rule_condition_queues_source == "users":
            input_email_address = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )

        elif self._rule_condition_queues_source == "queues":
            input_email_address = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )

        input_email_address.send_keys(action["details"]["email_address"])
