from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...interfaces import BrowserPort
    from ....rules.models import Rule
    from ....rules.models.triggers.action_based import AgentStateChangeDetails
    from ....logger.adapters import LogAdapter

from ....rules.enums import STATEEQUALITYOPERATOR
from time import sleep
import threading
from selenium.webdriver.common.by import By

from ..wrappers import ExecutorWrappers


class TriggerActionStateChangedExecutor:
    """
    Worker class responsible for handling stats-based conditions within rules.
    This worker interacts with the UI to set the equality operator, threshold, and queue sources
    for stats-based conditions using Selenium WebDriver.
    """

    def __init__(
        self,
        browser_port: BrowserPort,
        rule: Rule,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.browser_port = browser_port
        self._rule_condition_queues_source = "queues"
        self.logger = logger
        self.should_stop = should_stop
        self.rule = rule
        self.action_based_details: AgentStateChangeDetails = rule.trigger.details

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process the stats-based condition, including setting the equality operator,
        threshold, and queue sources. Emits the finished signal when complete.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )

        self.set_agent_and_aux()
        self.set_equality_operator()
        self.set_user_list()

    def set_state_changed_to(self, state):
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_Arrow")]',
        )
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_DropDown")]/div/ul/li',
            state,
        )

    def set_agent_aux(self, aux) -> None:
        """
        Sets the the aux code for the state changed to.
        """
        self.browser_port.wait_and_type(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateAuxCodeValue")]',
            aux,
        )

    def set_agent_and_aux(self) -> None:
        """
        Sets the agent state and aux code for the state changed to for the array of state.
        """

        for agent_changed in self.action_based_details.state:
            self.set_state_changed_to(agent_changed.state)
            self.set_agent_aux(agent_changed.aux)

            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_divParameters")]/div[1]/div[1]/div[3]/img',
            )
            sleep(1)

    def set_equality_operator(self) -> None:
        """
        Sets the the equality operator for the state changed to.
        """

        equality_operator = self.action_based_details.equality_operator
        self.logging(
            f"Setting equality operator to {equality_operator}.",
            "INFO",
        )
        if equality_operator == STATEEQUALITYOPERATOR.EQUAL_TO:
            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_ctl16_0")]',
            )

        elif equality_operator == STATEEQUALITYOPERATOR.NOT_EQUAL_TO:
            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_ctl16_1")]',
            )

    def set_user_list(self) -> None:
        """
        Sets the user list for the state changed to rule.
        """
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "user_filter_static_id_Arrow")]',
        )
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "user_filter_static_id_DropDown")]/div/ul/li',
            self.action_based_details.user_list,
        )
