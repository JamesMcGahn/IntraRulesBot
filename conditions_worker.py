from time import sleep

from PySide6.QtCore import QObject
from selenium.webdriver.common.by import By

from conditions_stats_worker import ConditionsStatsWorker
from web_element_interactions import WaitConditions, WebElementInteractions


class ConditionsWorker(QObject):

    def __init__(self, driver, rule):
        super().__init__()
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
            self.set_provider_category(condition)
            self.set_provider_instance(condition)
            self.set_provider_condition(condition)
            self.set_stats_based_condition(condition)
            self.add_additional_condition(i)

            ## Stats Condition

            sleep(3)

    def set_provider_category(self, condition):
        user_provider_category = condition["provider_category"]

        provider_category_select = self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
            user_provider_category,
        )

        if not provider_category_select:
            print(f"Unable to select provider category: {user_provider_category}")

        sleep(5)

    def set_provider_instance(self, condition):
        user_provider_instance = condition["provider_instance"]
        provider_instance_selection = self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
            user_provider_instance,
        )
        if not provider_instance_selection:
            print(f"Unable to select provider {user_provider_instance} ")

        sleep(5)

    def set_provider_condition(self, condition):
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

        sleep(5)

    def set_stats_based_condition(self, condition):
        condition_details = condition["details"]
        if condition_details["condition_type"] == "stats":
            stats_worker = ConditionsStatsWorker(self.driver, self, condition)
            stats_worker.do_work()

    def add_additional_condition(self, index):
        if (
            index != len(self.rule["conditions"]) - 1
            and len(self.rule["conditions"]) > 1
        ):
            add__addit_condition = self.wELI.wait_for_element(
                15,
                By.XPATH,
                '//*[contains(@id, "overlayContent_lblAddCondition")]',
                WaitConditions.CLICKABLE,
            )
            add__addit_condition.click()
