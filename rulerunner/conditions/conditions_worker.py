from time import sleep

from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..utils import WaitConditions, WebElementInteractions
from .conditions_stats_worker import ConditionsStatsWorker


class ConditionsWorker(QWorkerBase):

    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"
        self.wELI.send_msg.connect(self.logging)

    @property
    def rule_condition_queues_source(self):
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source):
        self._rule_condition_queues_source = source

    @ErrorWrappers.qworker_web_raise_error
    def do_work(self):
        self.log_thread()
        for i, condition in enumerate(self.rule["conditions"]):
            self.set_provider_category(condition, i)
            self.set_provider_instance(condition, i)
            self.set_provider_condition(condition, i)
            self.set_stats_based_condition(condition, i)
            self.add_additional_condition(i)

            sleep(2)
            self.finished.emit()

    def set_provider_category(self, condition, i):
        user_provider_category = condition["provider_category"]
        self.logging(f"Selecting provider category for Condition {i+1}...", "INFO")
        provider_category_select = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
            user_provider_category,
        )

        if not provider_category_select:
            raise ValueError(
                f"For Condition {i+1} - Unable to select provider category: {user_provider_category}"
            )

        sleep(2)

    def set_provider_instance(self, condition, i):
        self.logging(f"Selecting provider instance for Condition {i+1}...", "INFO")
        user_provider_instance = condition["provider_instance"]
        provider_instance_selection = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
            user_provider_instance,
        )
        if not provider_instance_selection:
            raise ValueError(
                f"For Condition {i+1} - Unable to select provider instance: {user_provider_instance}"
            )

        sleep(2)

    def set_provider_condition(self, condition, i):
        self.logging(f"Selecting condition selection for Condition {i+1}...", "INFO")
        user_provider_condition = condition["provider_condition"]
        provider_condition_selection = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
            user_provider_condition,
            5,
        )
        if not provider_condition_selection:
            raise ValueError(
                f"For Condition {i+1} - Unable to select provider condition: {user_provider_condition}"
            )

        sleep(2)

    def set_stats_based_condition(self, condition, index):
        condition_details = condition["details"]
        if condition_details["condition_type"] == "stats":
            stats_worker = ConditionsStatsWorker(self.driver, self, condition, index)
            stats_worker.send_logs.connect(self.logging)
            stats_worker.finished.connect(stats_worker.deleteLater)
            stats_worker.do_work()

    def add_additional_condition(self, index):
        if (
            index != len(self.rule["conditions"]) - 1
            and len(self.rule["conditions"]) > 1
        ):
            add__addit_condition = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_lblAddCondition")]',
                WaitConditions.CLICKABLE,
                raise_exception=True,
            )
            self.logging(f"Adding condition {index+2}...", "INFO")
            add__addit_condition.click()
