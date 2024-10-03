from time import sleep

from selenium.common.exceptions import (
    NoSuchFrameException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .actions import ActionsWorker
from .conditions import ConditionsWorker
from .triggers import TriggerWorker
from .utils import WaitConditions, WebElementInteractions, WorkerClass


class RuleWorker(WorkerClass):

    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)

    def do_work(self):
        try:
            addRuleBtn = self.wELI.wait_for_element(
                20,
                By.ID,
                "ctl00_ActionBarContent_rbAction_Add",
                WaitConditions.CLICKABLE,
                raise_exception=True,
            )
            if addRuleBtn:
                addRuleBtn.click()
                print("here")
                self.switch_to_rule_module()
                print("here 1")
                if self.is_tutorial_page_present():
                    self.logging("Tutorial Page is present...", "INFO")
                    self.next_page()
                print("here 2")
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

                self.finished.emit()
        except NoSuchFrameException:
            self.logging("Can't Find Frame. The window was closed.", "ERROR")
            self.error.emit()
        except WebDriverException as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            self.error.emit()
        except Exception as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            self.error.emit()

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
            raise_exception=True,
        )

    def submit_rule(self):
        rule_name = self.rule["rule_name"]
        self.logging(f"Submitting Rule - {rule_name}...", "INFO")
        submit_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        submit_btn.click()
        self.wait_for_dup_rule_alert()
        self.driver.switch_to.default_content()
        success_message = self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[contains(@id, "lblMessage")]',
            WaitConditions.VISIBILITY,
            raise_exception=False,
        )
        if "You have successfully added the Rule" in success_message.text:
            self.logging(f"Rule: {rule_name} has been created.", "INFO")

        else:
            self.logging(
                f"Recevied no success feedback. Cannot confirm if Rule: {rule_name} has been created.",
                "WARN",
            )

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
        sleep(2)
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
        sleep(2)
        self.logging("Switching the main frame", "INFO")
        self.driver.switch_to.default_content()

    def wait_for_dup_rule_alert(self):

        try:
            rule_name = self.rule["rule_name"]
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            if "A Rule with this name already exists" in alert.text:
                alert.accept()
                # TODO Ask user to update

                self.logging(
                    f"A Rule with the name {rule_name} already exists.", "ERROR"
                )
                raise ValueError

        except TimeoutException:
            self.logging(f"Rule: {rule_name} has been submitted.", "INFO")
