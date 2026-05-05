from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...interfaces import BrowserPort
    from ....rules.models import Rule
    from ....rules.models.conditions import ConditionStatsDetails

from ....rules.enums import QUEUESSOURCE

from selenium.webdriver.common.by import By
import threading
from base import ErrorWrappers


class ConditionsStatsExecutor:
    """
    Worker class responsible for handling stats-based conditions within rules.
    This worker interacts with the UI to set the equality operator, threshold, and queue sources
    for stats-based conditions using Selenium WebDriver.
    """

    def __init__(self, browser_port: BrowserPort, rule: Rule, index: int, logger):
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
        self.index = index
        self.condition = None
        self.logger = logger

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ErrorWrappers.qworker_web_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process the stats-based condition, including setting the equality operator,
        threshold, and queue sources. Emits the finished signal when complete.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )

        try:
            self.condition = self.rule.conditions[self.index]
        except IndexError as _:
            self.logging(
                f"Condition index {self.index} is out of range for {self.rule.rule_name}",
                "ERROR",
            )
            raise IndexError from IndexError

        condition_details: ConditionStatsDetails = self.condition.details

        # equality comparison dropdown
        self.set_equality_operator(condition_details)
        self.set_equality_threshold(condition_details)
        # Condition numeric value input to compare

        user_condition_queues = condition_details.queues_source
        if user_condition_queues == QUEUESSOURCE.QUEUES:
            self.set_queues_sources_queue()

    def set_equality_operator(self, condition_details: ConditionStatsDetails) -> None:
        """
        Sets the equality operator for the stats-based condition.
        """
        self.logging(
            f"Selecting stats equality comparison operator for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
        )

        # equality comparison operator selection
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_DropDown")]/div/ul/li',
            condition_details.equality_operator,
        )

    def set_equality_threshold(self, condition_details: ConditionStatsDetails) -> None:
        """
        Sets the equality threshold for the stats-based condition.
        """
        self.logging(
            f"Selecting stats threshold for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_type(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_tbExposedDataValue")]',
            condition_details.equality_threshold,
        )

    def set_queues_sources_queue(self) -> None:
        """
        Sets the queue source for the condition to "queues" and selects all queues.
        """
        self.logging(
            f"Selecting queue source as 'queues' for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl16_1")]',
        )

        self.logging(
            f"Selecting queue all listed queues for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl22_Arrow")]',
        )

        self.browser_port.click_all_items_in_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl22_DropDown")]/div/ul/li',
            retries=5,
            item_name="queues in queues list",
        )
