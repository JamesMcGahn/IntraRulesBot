import json
from time import sleep

from PySide6.QtCore import Signal
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

from actions_worker import ActionsWorker
from conditions_worker import ConditionsWorker
from keys import keys
from services.logger import Logger
from trigger_worker import TriggerWorker
from web_element_interactions import WaitConditions, WebElementInteractions
from worker_class import WorkerClass


class RuleWorker(WorkerClass):
    finished = Signal()

    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    def do_work(self):
        addRuleBtn = self.wELI.wait_for_element(
            20,
            By.ID,
            "ctl00_ActionBarContent_rbAction_Add",
            WaitConditions.CLICKABLE,
        )
        if addRuleBtn:
            addRuleBtn.click()
            self.switch_to_rule_module()

            if self.is_tutorial_page_present():
                self.logging("Tutorial Page is present...", "INFO")
                self.next_page()

            self.set_rule_name()
            self.start_trigger_page()
            self.next_page()
            self.start_conditions_page()
            self.next_page()
            self.start_actions_page()
            self.set_rule_category()
            self.switch_to_rule_module()
            self.next_page()
            self.submit_rule()
            # self.wait_for_dup_rule_alert()
            self.finished.emit()

    def start_trigger_page(self):
        trigger = TriggerWorker(self.driver, self.rule)
        trigger.send_logs.connect(self.logging)
        trigger.do_work()

    def start_conditions_page(self):
        self.conditions = ConditionsWorker(self.driver, self.rule)
        if "conditions" in self.rule and self.rule["conditions"]:
            self.conditions.send_logs.connect(self.logging)
            self.conditions.do_work()

    def start_actions_page(self):
        self.actions = ActionsWorker(self.driver, self.rule)
        if "actions" in self.rule and self.rule["actions"]:
            self.actions.rule_condition_queues_source = (
                self.conditions.rule_condition_queues_source
            )
            self.actions.send_logs.connect(self.logging)
            self.actions.do_work()

    def switch_to_rule_module(self):
        self.logging("Switching to the Rule Modal...", "INFO")
        self.wELI.switch_to_frame(20, By.NAME, "RadWindowAddEditRule")

    def set_rule_name(self):
        self.logging("Setting the Rule Name...", "INFO")
        rule_name_input = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
            WaitConditions.VISIBILITY,
        )
        rule_name_input.send_keys(self.rule["rule_name"])

    def next_page(self):
        self.logging("Navigating to the Next Page...", "INFO")
        continue_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
        )
        sleep(2)
        continue_btn.click()

    def is_tutorial_page_present(self):
        return self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
            WaitConditions.CLICKABLE,
        )

    def submit_rule(self):
        self.logging(f"Submitting Rule - {self.rule["rule_name"]}...", "INFO")
        submit_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
            WaitConditions.CLICKABLE,
        )
        submit_btn.click()
        self.wait_for_dup_rule_alert()
        self.driver.switch_to.default_content()
        success_message = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "lblMessage")]',
            WaitConditions.VISIBILITY,
        )
        if "You have successfully added the Rule" in success_message.text:
            self.logging(f"Rule: {self.rule["rule_name"]} has been created.","INFO")

        else:
            self.logging(f"Recevied no success feedback. Cannot confirm if Rule: {self.rule["rule_name"]} has been created.","WARN")


    def set_rule_category(self):
        self.logging("Setting the rule category","INFO")
        rule_settings_hamburger = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a',
            WaitConditions.CLICKABLE,
        )
        rule_settings_hamburger.click()
        sleep(2)
        self.driver.switch_to.default_content()
        self.wELI.switch_to_frame(20, By.NAME, "RadWindowAddEditRuleSettings")
        rule_category_dropdown_arrow = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_Arrow")]',
            WaitConditions.CLICKABLE,
        )
        rule_category_dropdown_arrow.click()
        rule_category_selection = self.rule["rule_category"]
        self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            rule_category_selection
        )
        sleep(2)
        self.logging("Switching the main frame", "INFO")
        self.driver.switch_to.default_content()

    def wait_for_dup_rule_alert(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            if alert.text == "A Rule with this name already exists":
                alert.accept()
                # TODO Ask user to update

                self.logging(
                                 f"A Rule with the name {self.rule["rule_name"]} already exists.",
                                 "ERROR"
                           )
                raise ValueError(alert.text)

        except TimeoutException:
            self.logging(f"Rule: {self.rule["rule_name"]} has been submitted.","INFO")