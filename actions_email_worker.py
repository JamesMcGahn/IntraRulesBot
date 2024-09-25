from time import sleep

from PySide6.QtCore import QObject
from selenium.webdriver.common.by import By

from web_element_interactions import WaitConditions, WebElementInteractions


class ActionsEmailWorker(QObject):
    def __init__(self, driver, actions_worker, action, rule):
        super().__init__()
        self.driver = driver
        self.action = action
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = actions_worker.rule_condition_queues_source

    def do_work(self):
        self.click_email_settings_page()
        self.set_email_subject(self.rule["rule_name"])
        self.set_email_message(self.action)
        self.click_next_page()
        self.set_email_address(self.action)

    def click_email_settings_page(self):

        email_page_settings_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_lblSettings")]',
            WaitConditions.CLICKABLE,
        )
        email_page_settings_btn.click()

    def set_email_subject(self, rule_name):

        email_subject = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_ctl05")]',
            WaitConditions.VISIBILITY,
        )
        email_subject.send_keys(rule_name)

    def set_email_message(self, action):

        if "frequency_based" in self.rule:
            email_message = self.wELI.wait_for_element(
                15,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
                WaitConditions.VISIBILITY,
            )
        else:
            email_message = self.wELI.wait_for_element(
                15,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl13")]',
                WaitConditions.VISIBILITY,
            )

        email_message.send_keys(action["details"]["email_body"])
        sleep(3)

    def click_next_page(self):
        continue_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
        )
        continue_btn.click()

    def set_email_address(self, action):
        select_email_individual = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1")]',
            WaitConditions.CLICKABLE,
        )
        select_email_individual.click()

        if self._rule_condition_queues_source == "users":
            input_email_address = self.wELI.wait_for_element(
                15,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                WaitConditions.VISIBILITY,
            )

        elif self._rule_condition_queues_source == "queues":
            input_email_address = self.wELI.wait_for_element(
                15,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                WaitConditions.VISIBILITY,
            )

        input_email_address.send_keys(action["details"]["email_address"])
