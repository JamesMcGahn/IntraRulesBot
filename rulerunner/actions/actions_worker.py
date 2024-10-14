from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..actions import ActionsEmailWorker
from ..utils import WaitConditions, WebElementInteractions


class ActionsWorker(QWorkerBase):
    """
    Worker class responsible for handling multiple actions within rules.
    This worker interacts with the UI to set up Action's provider categories, instances,
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

    @property
    def rule_condition_queues_source(self) -> str:
        """
        Gets the source of the rule condition (either "users" or "queues").

        Returns:
            str: The current rule condition queues source.
        """
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source):
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
        Executes the steps required to process each action within the rule, including setting
        provider categories, instances, conditions, and executing email actions. Emits the
        finished signal when the work is complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()
        for i, action in enumerate(self.rule["actions"]):

            self.set_provider_category(action, i)
            self.set_provider_instance(action, i)
            self.set_provider_condition(action, i)
            self.set_email_action(action, self.rule, i)
            self.add_additional_action(i)
            self.finished.emit()

    def set_provider_category(self, action: dict, i: int) -> None:
        """
        Selects the provider category for the specified action.

        Args:
            action (dict): The action data containing the provider category.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Selecting provider category for Action {i+1}...", "INFO")
        user_action_category_selection = action["provider_category"]

        action_category_dropdown = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
            user_action_category_selection,
        )
        if not action_category_dropdown:
            raise ValueError(
                f"For Condition {i+1} - Unable to select provider category: {action_category_dropdown}"
            )
        sleep(1)

    def set_provider_instance(self, action: dict, i: int) -> None:
        """
        Selects the provider instance for the specified action.

        Args:
            action (dict): The action data containing the provider instance.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Selecting provider instance for Action {i+1}...", "INFO")
        user_action_provider_instance = action["provider_instance"]

        action_provider_dropdown = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuProviderInstance")]/ul/li',
            user_action_provider_instance,
        )
        if not action_provider_dropdown:
            raise ValueError(
                f"For Action {i+1} - Unable to select provider instance: {user_action_provider_instance}"
            )

        sleep(1)

    def set_provider_condition(self, action: dict, i: int) -> None:
        """
        Selects the provider condition for the specified action.

        Args:
            action (dict): The action data containing the provider condition.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Selecting condition selection for Action {i+1}...", "INFO")
        user_action_selection = action["provider_condition"]
        action_selection_dropdown = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuItem")]/ul/li',
            user_action_selection,
        )
        if not action_selection_dropdown:
            raise ValueError(
                f"For Condition {i+1} - Unable to select provider condition: {user_action_selection}"
            )

    def set_email_action(self, action: dict, rule: dict, i: int) -> None:
        """
        Executes the email action for the specified action if the action type is email.

        Args:
            action (dict): The action data.
            rule (dict): The rule data.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        if action["details"]["action_type"] == "email":
            actions_worker = ActionsEmailWorker(self.driver, self, action, rule, i)
            actions_worker.send_logs.connect(self.logging)
            self.finished.connect(actions_worker.deleteLater)
            actions_worker.do_work()

    def add_additional_action(self, index: int) -> None:
        """
        Adds additional actions to the UI if more than one action exists.

        Args:
            index (int): The index of the current action.

        Returns:
            None: This function does not return a value.
        """
        if index != len(self.rule["actions"]) - 1 and len(self.rule["actions"]) > 1:
            add__addit_action = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_lblAddAction")]',
                WaitConditions.CLICKABLE,
                raise_exception=True,
            )
            self.logging(f"Adding condition {index+2}...", "INFO")
            add__addit_action.click()
            sleep(1)
