from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..utils import WaitConditions, WebElementInteractions
from .conditions_stats_worker import ConditionsStatsWorker


class ConditionsWorker(QWorkerBase):
    """
    Worker class responsible for handling conditions within rules.
    This worker interacts with the UI to set up provider categories,
    instances, conditions, and stats-based conditions using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        rule (dict): The rule data that contains the list of conditions.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        _rule_condition_queues_source (str): The source of the rule condition, initially set to "queues".

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        rule (dict): The rule data used to configure the conditions.
    """

    def __init__(self, driver: webdriver.Chrome, rule: dict):
        """
        Initializes the ConditionsWorker with the provided driver and rule data.
        Sets up the necessary connections for interacting with web elements.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data used to configure the conditions.
        """
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"
        self.wELI.send_msg.connect(self.logging)

    @property
    def rule_condition_queues_source(self) -> str:
        """
        Gets the source of the rule condition (either "users" or "queues").

        Returns:
            str: The current rule condition queues source.
        """
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source: str) -> None:
        """
        Sets the source of the rule condition (either "users" or "queues").

        Args:
            source (str): The new rule condition source.

        Returns:
            None: This function does not return a value.
        """
        self._rule_condition_queues_source = source

    @ErrorWrappers.qworker_web_raise_error
    def do_work(self) -> None:
        """
        Executes the steps required to process each condition within the rule, including setting
        provider categories, instances, conditions, and stats-based conditions. Emits the
        finished signal when the work is complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()
        for i, condition in enumerate(self.rule["conditions"]):
            self.set_provider_category(condition, i)
            self.set_provider_instance(condition, i)
            self.set_provider_condition(condition, i)
            self.set_stats_based_condition(condition, i)
            self.add_additional_condition(i)

            sleep(1)
            self.finished.emit()

    def set_provider_category(self, condition: dict, i: int) -> None:
        """
        Selects the provider category for the specified condition.

        Args:
            condition (dict): The condition data containing the provider category.
            i (int): The index of the condition in the list.

        Returns:
            None: This function does not return a value.
        """
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

        sleep(1)

    def set_provider_instance(self, condition: dict, i: int) -> None:
        """
        Selects the provider instance for the specified condition.

        Args:
            condition (dict): The condition data containing the provider instance.
            i (int): The index of the condition in the list.

        Returns:
            None: This function does not return a value.
        """
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

        sleep(1)

    def set_provider_condition(self, condition: dict, i: int) -> None:
        """
        Selects the provider condition for the specified condition.

        Args:
            condition (dict): The condition data containing the provider condition.
            i (int): The index of the condition in the list.

        Returns:
            None: This function does not return a value.
        """
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

        sleep(1)

    def set_stats_based_condition(self, condition: dict, index: int) -> None:
        """
        Sets a stats-based condition if the condition type is 'stats'.

        Args:
            condition (dict): The condition data containing the stats-based condition details.
            index (int): The index of the condition in the list.

        Returns:
            None: This function does not return a value.
        """
        condition_details = condition["details"]
        if condition_details["condition_type"] == "stats":
            self.stats_worker = ConditionsStatsWorker(
                self.driver, self, condition, index
            )
            self.stats_worker.send_logs.connect(self.logging)
            self.finished.connect(self.stats_worker.deleteLater)
            self.stats_worker.do_work()

    def add_additional_condition(self, index: int) -> None:
        """
        Adds additional conditions to the UI if more than one condition exists.

        Args:
            index (int): The index of the current condition.

        Returns:
            None: This function does not return a value.
        """
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
