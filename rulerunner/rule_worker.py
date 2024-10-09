from time import sleep

from PySide6.QtCore import Signal
from selenium.common.exceptions import (
    NoSuchFrameException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base import QWorkerBase
from base.exceptions import DuplicateRuleName

from .actions import ActionsWorker
from .conditions import ConditionsWorker
from .triggers import TriggerWorker
from .utils import WaitConditions, WebElementInteractions


class RuleWorker(QWorkerBase):
    finished = Signal(str)
    error = Signal(bool)

    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)
        self.rule_rename_attempts = 0
        self.rule_name = rule["rule_name"]

    def do_work(self):
        try:
            self.log_thread()
            addRuleBtn = self.wELI.wait_for_element(
                20,
                By.ID,
                "ctl00_ActionBarContent_rbAction_Add",
                WaitConditions.CLICKABLE,
                raise_exception=True,
            )
            if addRuleBtn:
                addRuleBtn.click()

                self.switch_to_rule_module()

                if self.is_tutorial_page_present():
                    self.logging("Tutorial Page is present...", "INFO")
                    self.next_page()

                self.set_rule_name(self.rule_name)
                self.start_trigger_page()
                self.next_page()
                self.start_conditions_page()
                self.next_page()
                self.start_actions_page()
                self.set_rule_category()
                self.switch_to_rule_module()
                self.next_page()
                self.submit_rule()

                if self.rule_rename_attempts == 0:
                    self.finished.emit(self.rule_name)
                else:
                    old_rule_name = self.rule["rule_name"]
                    self.finished.emit(f"{old_rule_name} renamed {self.rule_name}")
        except DuplicateRuleName:
            self.error.emit(False)

        except NoSuchFrameException:
            self.logging("Can't Find Frame. The window was closed.", "ERROR")
            self.error.emit(True)
        except WebDriverException as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            self.error.emit(True)
        except Exception as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            self.error.emit(True)

    def start_trigger_page(self):
        self.trigger = TriggerWorker(self.driver, self.rule)
        self.trigger.send_logs.connect(self.logging)
        self.trigger.finished.connect(self.trigger.deleteLater)
        self.trigger.do_work()

    def start_conditions_page(self):
        self.conditions = ConditionsWorker(self.driver, self.rule)
        if "conditions" in self.rule and self.rule["conditions"]:
            self.conditions.send_logs.connect(self.logging)
            self.conditions.finished.connect(self.conditions.deleteLater)
            self.conditions.do_work()

    def start_actions_page(self):
        self.actions = ActionsWorker(self.driver, self.rule)
        if "actions" in self.rule and self.rule["actions"]:
            self.actions.rule_condition_queues_source = (
                self.conditions.rule_condition_queues_source
            )
            self.actions.send_logs.connect(self.logging)
            self.actions.finished.connect(self.actions.deleteLater)
            self.actions.do_work()

    def switch_to_rule_module(self):
        self.logging("Switching to the Rule Modal...", "INFO")
        self.wELI.switch_to_frame(20, By.NAME, "RadWindowAddEditRule")

    def set_rule_name(self, rule_name):
        self.logging("Setting the Rule Name...", "INFO")
        rule_name_input = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
            WaitConditions.VISIBILITY,
        )
        rule_name_input.clear()
        rule_name_input.send_keys(rule_name)

    def next_page(self):
        self.logging("Navigating to the Next Page...", "INFO")
        continue_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
        )
        sleep(1)
        continue_btn.click()

    def is_tutorial_page_present(self):
        return self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )

    def submit_rule(self):

        self.logging(f"Submitting Rule - {self.rule_name }...", "INFO")
        submit_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )

        def handle_duplicate_alert():
            for _ in range(2):

                # Retry twice before giving up
                alert = self.wait_for_dup_rule_alert(10)
                if alert:
                    self.rename_rule()
                    self.logging(
                        f"Retrying Rule Submission for renamed rule - {self.rule_name }...",
                        "INFO",
                    )
                    submit_btn.click()
                else:
                    return False  # No alert found, submission is successful
            return True

        submit_btn.click()

        if handle_duplicate_alert():
            if self.wait_for_dup_rule_alert(5):
                self.logging(
                    f"Rule '{self.rule_name}' could not be submitted after multiple retries.",
                    "ERROR",
                )
                raise DuplicateRuleName

        self.driver.switch_to.default_content()
        self.success_message()

    def rename_rule(self):
        self.rule_rename_attempts += 1
        old_rule_name = self.rule["rule_name"]
        self.rule_name = f"{old_rule_name}-{self.rule_rename_attempts}"
        self.logging(
            f"Trying to rename rule: {old_rule_name} as {self.rule_name}",
            "ERROR",
        )
        self.set_rule_name(self.rule_name)

    def success_message(self):
        self.wELI.wait_for_element(
            20,
            By.ID,
            "ctl00_ActionBarContent_rbAction_Add",
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )

        self.logging(f"Rule: {self.rule_name} has been created.", "INFO")

    def set_rule_category(self):
        self.logging("Setting the rule category", "INFO")
        rule_settings_hamburger = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        rule_settings_hamburger.click()
        sleep(1)
        self.driver.switch_to.default_content()
        self.wELI.switch_to_frame(20, By.NAME, "RadWindowAddEditRuleSettings")
        rule_category_dropdown_arrow = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_Arrow")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        rule_category_dropdown_arrow.click()
        rule_category_selection = self.rule["rule_category"]
        self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            rule_category_selection,
            raise_exception=True,
        )
        sleep(1)
        self.logging("Switching the main frame", "INFO")
        self.driver.switch_to.default_content()

    def wait_for_dup_rule_alert(self, wait_time):

        try:
            WebDriverWait(self.driver, wait_time).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            if "A Rule with this name already exists" in alert.text:

                self.logging(
                    f"A Rule with the name {self.rule_name} already exists.", "ERROR"
                )
                self.logging(
                    "Accepting window alert notifying of duplicate rule name.", "INFO"
                )
                alert.accept()

                if alert:
                    return True

        except TimeoutException:
            self.logging(f"Rule: {self.rule_name} has been submitted.", "INFO")
            return False
