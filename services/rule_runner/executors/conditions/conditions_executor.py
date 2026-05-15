from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ....browser.ports import FramePort
    from ....rules.models import Rule
    from ....rules.models.conditions import Condition
    from ....logger.adapters import LogAdapter

from time import sleep
import threading
from ..wrappers import ExecutorWrappers

from .conditions_stats_executor import ConditionsStatsExecutor
from ....rules.enums import CONDITIONDETAILTYPE


class ConditionsExecutor:
    """
    Worker class responsible for handling conditions within rules.
    This worker interacts with the UI to set up provider categories,
    instances, conditions, and stats-based conditions using Selenium WebDriver.
    """

    def __init__(
        self,
        frame_port: FramePort,
        rule: Rule,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.frame_port = frame_port
        self.rule = rule
        self.logger = logger
        self.should_stop = should_stop
        self.condition_type_reg = {CONDITIONDETAILTYPE.STATS: ConditionsStatsExecutor}

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process each condition within the rule, including setting
        provider categories, instances, conditions, and stats-based conditions. Emits the
        finished signal when the work is complete.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        for i, condition in enumerate(self.rule.conditions):
            self.set_provider_category(condition, i)
            self.set_provider_instance(condition, i)
            self.set_provider_condition(condition, i)
            self.execute_details_type(condition.details.condition_type, self.rule, i)
            self.add_additional_condition(i)

            sleep(1)

    def set_provider_category(self, condition: Condition, index: int) -> None:
        """
        Selects the provider category for the specified condition.
        """
        self.logging(f"Selecting provider category for Condition {index+1}...", "INFO")

        self.frame_port.select_exact_item_from_list(
            '//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
            condition.provider_category,
        )

    def set_provider_instance(self, condition: Condition, index: int) -> None:
        """
        Selects the provider instance for the specified condition.
        """
        self.logging(f"Selecting provider instance for Condition {index+1}...", "INFO")
        self.frame_port.select_exact_item_from_list(
            '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
            condition.provider_instance,
        )

    def set_provider_condition(self, condition: Condition, index: int) -> None:
        """
        Selects the provider condition for the specified condition.
        """
        self.logging(
            f"Selecting condition selection for Condition {index+1}...", "INFO"
        )
        self.frame_port.select_exact_item_from_list(
            '//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
            condition.provider_condition,
        )

    def execute_details_type(
        self, condition_type: CONDITIONDETAILTYPE, rule: Rule, index: int
    ):
        executor = self.condition_type_reg.get(condition_type)
        if not executor:
            msg = f"{condition_type} is not a supported trigger action"
            self.logging(msg, "ERROR")
            raise ValueError(msg)

        executor(self.frame_port, rule, index, self.logger, self.should_stop).execute()

    def add_additional_condition(self, index: int) -> None:
        """
        Adds additional conditions to the UI if more than one condition exists.
        """
        if index != len(self.rule.conditions) - 1 and len(self.rule.conditions) > 1:
            self.logging(f"Adding condition {index+2}...", "INFO")
            self.frame_port.click('[id*="overlayContent_lblAddCondition"]')
