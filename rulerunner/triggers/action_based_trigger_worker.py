from time import sleep

from PySide6.QtCore import Signal, Slot
from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..utils import WebElementInteractions


class ActionBasedTriggerWorker(QWorkerBase):
    """
    Worker class responsible for handling Action Based Triggers within rules.
    This worker interacts with the UI to set up Action Based Triggers's provider categories, instances,
    conditions, and email actions using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        rule (dict): The rule data that contains the list of actions.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        _rule_condition_queues_source (str): The source of the rule condition, initially set to "queues".

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        rule (dict): The rule data used to configure the actions.
    """

    start_work = Signal()

    def __init__(self, driver: webdriver.Chrome, rule: dict):
        """
        Initializes the ActionsWorker with the provided driver and rule data.
        Sets up the necessary connections for interacting with web elements.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data used to configure the actions.
        """
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"
        self.wELI.send_msg.connect(self.logging)
        self.start_work.connect(self.do_work)

    @ErrorWrappers.qworker_web_raise_error
    @Slot()
    def do_work(self) -> None:
        """
        Executes the steps required to process each Action Based Trigger within the rule, including setting
        provider categories, instances, conditions, and executing email actions. Emits the
        finished signal when the work is complete.

        Returns:
            None: This function does not return a value.
        """

        action_based = self.rule["action_based"]
        self.set_provider_category(action_based)
        self.set_provider_instance(action_based)
        self.set_provider_condition(action_based)

    def set_provider_category(self, action_trigger: dict) -> None:
        """
        Selects the provider category for the specified action.
        Args:
            action_trigger (dict): The action trigger data containing the provider category.
        Returns:
            None: This function does not return a value.
        """
        self.logging("Selecting provider category for Action Trigger", "INFO")
        user_action_trigger_category_selection = action_trigger["provider_category"]

        action_trigger_category_dropdown = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
            user_action_trigger_category_selection,
        )
        if not action_trigger_category_dropdown:
            raise ValueError(
                f"Action Trigger - Unable to select provider category: {user_action_trigger_category_selection}"
            )
        sleep(1)

    def set_provider_instance(self, action_trigger: dict) -> None:
        """
        Selects the provider instance for the specified condition.

        Args:
            action_trigger (dict): The action trigger data containing the provider instance.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Selecting provider instance for Action Trigger", "INFO")
        user_provider_instance = action_trigger["provider_instance"]
        provider_instance_selection = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
            user_provider_instance,
        )
        if not provider_instance_selection:
            raise ValueError(
                f"Action Trigger - Unable to select provider instance: {user_provider_instance}"
            )

        sleep(1)

    def set_provider_condition(self, action_trigger: dict) -> None:
        """
        Selects the provider condition for the specified condition.

        Args:
            action_trigger (dict): The action_trigger data containing the provider condition.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Selecting condition selection for Action Trigger", "INFO")
        user_provider_condition = action_trigger["provider_condition"]
        provider_condition_selection = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
            user_provider_condition,
            5,
        )
        if not provider_condition_selection:
            raise ValueError(
                f"Action Trigger - Unable to select provider condition: {user_provider_condition}"
            )

        sleep(1)
