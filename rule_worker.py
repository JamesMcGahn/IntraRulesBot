import json
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

from actions_worker import ActionsWorker
from conditions_worker import ConditionsWorker
from keys import keys
from services.logger import Logger
from trigger_worker import TriggerWorker
from web_element_interactions import WaitConditions, WebElementInteractions


class RuleWorker(QObject):
    finished = Signal()

    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)

    def do_work(self):
        addRuleBtn = self.wELI.wait_for_element(
            10,
            By.ID,
            "ctl00_ActionBarContent_rbAction_Add",
            WaitConditions.CLICKABLE,
        )
        if addRuleBtn:
            addRuleBtn.click()
            self.switch_to_rule_module()

            if self.is_tutorial_page_present():
                self.next_page()

            self.set_rule_name()
            self.start_trigger_page()
            self.next_page()
            self.start_conditions_page()
            self.next_page()
            self.start_actions_page()
            self.set_rule_category()
            self.next_page()
            self.submit_rule()
            # self.wait_for_dup_rule_alert()
            self.finished.emit()

    def start_trigger_page(self):
        trigger = TriggerWorker(self.driver, self.rule)
        trigger.do_work()

    def start_conditions_page(self):
        self.conditions = ConditionsWorker(self.driver, self.rule)
        if "conditions" in self.rule and self.rule["conditions"]:
            self.conditions.do_work()

    def start_actions_page(self):
        self.actions = ActionsWorker(self.driver, self.rule)
        if "actions" in self.rule and self.rule["actions"]:
            self.actions.rule_condition_queues_source = (
                self.conditions.rule_condition_queues_source
            )
            self.actions.do_work()

    def switch_to_rule_module(self):
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "RadWindowAddEditRule"))
        )

    def set_rule_name(self):
        rule_name_input = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
            WaitConditions.VISIBILITY,
        )
        rule_name_input.send_keys(self.rule["rule_name"])

    def next_page(self):
        continue_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
        )
        sleep(3)
        continue_btn.click()

    def is_tutorial_page_present(self):
        return self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
            WaitConditions.CLICKABLE,
        )

    def submit_rule(self):
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
            Logger().insert(f"Rule: {self.rule["rule_name"]} has been created.","INFO")
        else:
            Logger().insert(f"Recevied no success feedback. Cannot confirm if Rule: {self.rule["rule_name"]} has been created.","WARN")



    def set_rule_category(self):
        rule_settings_hamburger = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a',
            WaitConditions.CLICKABLE,
        )
        rule_settings_hamburger.click()
        sleep(3)
        self.driver.switch_to.default_content()
        self.wELI.switch_to_frame(10, By.NAME, "RadWindowAddEditRuleSettings")
        rule_category_dropdown_arrow = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_Arrow")]',
            WaitConditions.CLICKABLE,
        )
        rule_category_dropdown_arrow.click()

        self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            "Other - Admin",
        )
        sleep(3)
        self.driver.switch_to.default_content()
        self.wELI.switch_to_frame(10, By.NAME, "RadWindowAddEditRule")

    def wait_for_dup_rule_alert(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            if alert.text == "A Rule with this name already exists":
                alert.accept()
                                # TODO Ask user to update
                                
                Logger().insert(
                                f"A Rule with the name {self.rule["rule_name"]} already exists.",
                                "ERROR",
                            )   
                raise ValueError(alert.text)
                            
        except TimeoutException:
            Logger().insert(f"Rule: {self.rule["rule_name"]} has been submitted.","INFO")