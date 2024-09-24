import json
from time import sleep

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

from keys import keys
from login_manager import LoginManager
from services.logger import Logger
from web_element_interactions import WaitConditions, WebElementInteractions


class ConditionsWorker:

    def __init__(self, driver, rule):
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"

    @property
    def rule_condition_queues_source(self):
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source):
        self._rule_condition_queues_source = source

    def do_work(self):
        for i, condition in enumerate(self.rule["conditions"]):

            user_provider_category = condition["provider_category"]

            provider_category_select = self.wELI.select_item_from_list(
                10,
                By.XPATH,
                '//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
                user_provider_category,
            )

            if not provider_category_select:
                print(f"Unable to select provider category: {user_provider_category}")
                return
            sleep(5)
            # ---> Select Provider Instance
            user_provider_instance = condition["provider_instance"]
            provider_instance_selection = self.wELI.select_item_from_list(
                10,
                By.XPATH,
                '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
                user_provider_instance,
            )
            if not provider_instance_selection:
                print(f"Unable to select provider {user_provider_instance} ")
                return
            # TODO - handle potential value error
            sleep(5)
            # ---> Select Provider Condition
            user_provider_condition = condition["provider_condition"]
            provider_condition_selection = self.wELI.select_item_from_list(
                10,
                By.XPATH,
                '//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
                user_provider_condition,
                5,
            )
            if not provider_condition_selection:
                print(
                    f"Cannot find. Please check that - {user_provider_condition} - is a listed condition for the provider"
                )
                return
            sleep(5)

            ## Stats Condition
            condition_details = condition["details"]
            if condition_details["condition_type"] == "stats":
                # equality comparison dropdown
                agents_in_after_call_eq_drop = self.wELI.wait_for_element(
                    10,
                    By.XPATH,
                    '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
                    WaitConditions.CLICKABLE,
                )
                agents_in_after_call_eq_drop.click()

                # equality comparison operator selection
                user_agents_in_after_call_eq = condition_details["equality_operator"]
                agents_in_after_call_eq = self.wELI.select_item_from_list(
                    10,
                    By.XPATH,
                    '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_DropDown")]/div/ul/li',
                    user_agents_in_after_call_eq,
                )
                if not agents_in_after_call_eq:
                    print(
                        f"Cant not find {user_agents_in_after_call_eq}. Make sure the comparison operator text is correct"
                    )
                    return

                # Condition numeric value input to compare
                agents_in_after_call_eq_condition = self.wELI.wait_for_element(
                    15,
                    By.XPATH,
                    '//*[contains(@id, "overlayContent_conditionParameters_tbExposedDataValue")]',
                    WaitConditions.VISIBILITY,
                )

                user_agents_in_after_call_eq_condition = condition_details[
                    "equality_threshold"
                ]

                agents_in_after_call_eq_condition.send_keys(
                    user_agents_in_after_call_eq_condition
                )

                user_condition_queues = condition_details["queues_source"]
                if user_condition_queues == "users":
                    # TODO: need getter when made into fn
                    self._rule_condition_queues_source = "users"

                elif user_condition_queues == "queues":

                    queues_radio_btn = self.wELI.wait_for_element(
                        15,
                        By.XPATH,
                        '//*[contains(@id, "overlayContent_conditionParameters_ctl16_1")]',
                        WaitConditions.CLICKABLE,
                    )
                    queues_radio_btn.click()

                    user_queues_dropdown_btn = self.wELI.wait_for_element(
                        15,
                        By.XPATH,
                        '//*[contains(@id, "overlayContent_conditionParameters_ctl22_Arrow")]',
                        WaitConditions.CLICKABLE,
                    )
                    user_queues_dropdown_btn.click()

                    queues_list = self.wELI.click_all_items_in_list(
                        10,
                        By.XPATH,
                        '//*[contains(@id, "overlayContent_conditionParameters_ctl22_DropDown")]/div/ul/li',
                        5,
                        "queues in queues list",
                    )

                    if not queues_list:
                        return

                if (
                    i != len(self.rule["conditions"]) - 1
                    and len(self.rule["conditions"]) > 1
                ):
                    add__addit_condition = self.wELI.wait_for_element(
                        15,
                        By.XPATH,
                        '//*[contains(@id, "overlayContent_lblAddCondition")]',
                        WaitConditions.CLICKABLE,
                    )
                    add__addit_condition.click()

            sleep(3)
