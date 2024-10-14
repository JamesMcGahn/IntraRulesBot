from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..utils import WaitConditions, WebElementInteractions


class ConditionsStatsWorker(QWorkerBase):
    """
    Worker class responsible for handling stats-based conditions within rules.
    This worker interacts with the UI to set the equality operator, threshold, and queue sources
    for stats-based conditions using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        condition (dict): The condition data that contains details such as equality operator and threshold.
        index (int): The index of the current condition in the list of conditions.
        conditions_worker (ConditionsWorker): The parent worker managing the conditions.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        _rule_condition_queues_source (str): The source of the rule condition, initially set to "queues".

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        conditions_worker (ConditionsWorker): The parent worker managing the conditions.
        condition (dict): The stats-based condition data.
        index (int): The index of the current condition.
    """

    def __init__(
        self, driver: webdriver.Chrome, conditions_worker, condition: dict, index: int
    ):
        """
        Initializes the ConditionsStatsWorker with the provided driver, condition, index, and conditions_worker.
        Connects logging to web element interactions and sets up internal references for stats-based condition processing.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            conditions_worker (ConditionsWorker): The parent worker managing the conditions.
            condition (dict): The stats-based condition data.
            index (int): The index of the current condition.
        """
        super().__init__()
        self.driver = driver
        self.condition = condition
        self.index = index
        self.conditions_worker = conditions_worker
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"
        self.wELI.send_msg.connect(self.logging)

    @ErrorWrappers.qworker_web_raise_error
    def do_work(self) -> None:
        """
        Executes the steps required to process the stats-based condition, including setting the equality operator,
        threshold, and queue sources. Emits the finished signal when complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()
        condition_details = self.condition["details"]

        # equality comparison dropdown
        self.set_equality_operator(condition_details)
        self.set_equality_threshold(condition_details)
        # Condition numeric value input to compare

        user_condition_queues = condition_details["queues_source"]
        if user_condition_queues == "users":
            self.set_queues_sources_users()

        elif user_condition_queues == "queues":
            self.set_queues_sources_queue()

        self.finished.emit()

    def set_equality_operator(self, condition_details: dict) -> None:
        """
        Sets the equality operator for the stats-based condition.

        Args:
            condition_details (dict): The condition details containing the equality operator.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting stats equality comparison operator for Condition {self.index+1}...",
            "INFO",
        )
        agents_in_after_call_eq_drop = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        agents_in_after_call_eq_drop.click()

        # equality comparison operator selection
        user_agents_in_after_call_eq = condition_details["equality_operator"]
        agents_in_after_call_eq = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_DropDown")]/div/ul/li',
            user_agents_in_after_call_eq,
        )
        if not agents_in_after_call_eq:
            raise ValueError(
                f"For Condition {self.index+1} - Cant not find {user_agents_in_after_call_eq}. Make sure the comparison operator text is correct"
            )

    def set_equality_threshold(self, condition_details: dict) -> None:
        """
        Sets the equality threshold for the stats-based condition.

        Args:
            condition_details (dict): The condition details containing the equality threshold.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting stats threshold for Condition {self.index+1}...",
            "INFO",
        )
        agents_in_after_call_eq_condition = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_tbExposedDataValue")]',
            WaitConditions.VISIBILITY,
            raise_exception=True,
        )

        user_agents_in_after_call_eq_condition = condition_details["equality_threshold"]

        agents_in_after_call_eq_condition.send_keys(
            user_agents_in_after_call_eq_condition
        )

    def set_queues_sources_users(self) -> None:
        """
        Sets the queue source for the condition to "users".

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting queue source as 'users' for Condition {self.index+1}...",
            "INFO",
        )
        self.conditions_worker.rule_condition_queues_source = "users"

    def set_queues_sources_queue(self) -> None:
        """
        Sets the queue source for the condition to "queues" and selects all queues.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting queue source as 'queues' for Condition {self.index+1}...",
            "INFO",
        )
        queues_radio_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl16_1")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        queues_radio_btn.click()
        self.logging(
            f"Selecting queue all listed queues for Condition {self.index+1}...",
            "INFO",
        )
        user_queues_dropdown_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl22_Arrow")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        user_queues_dropdown_btn.click()
        queues_list = self.wELI.click_all_items_in_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl22_DropDown")]/div/ul/li',
            5,
            "queues in queues list",
        )
        if not queues_list:
            raise ValueError(
                f"For Condition {self.index+1} - unable to select all queues"
            )
