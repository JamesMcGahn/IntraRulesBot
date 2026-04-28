from time import sleep

from PySide6.QtCore import Signal, Slot
from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers, QWorkerBase

from ..utils import WaitConditions, WebElementInteractions


class TriggerActionStateWorker(QWorkerBase):
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

    start_work = Signal()

    def __init__(self, driver: webdriver.Chrome, action_based: dict):
        """
        Initializes the TriggerActionStateWorker with the provided driver, condition, index, and conditions_worker.
        Connects logging to web element interactions and sets up internal references for stats-based condition processing.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            action_based (dict): The stats-based action_based data.
            index (int): The index of the current condition.
        """
        super().__init__()
        self.driver = driver
        self.action_based = action_based
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"
        self.wELI.send_msg.connect(self.logging)
        self.start_work.connect(self.do_work)

    @ErrorWrappers.qworker_web_raise_error
    @Slot()
    def do_work(self) -> None:
        """
        Executes the steps required to process the stats-based condition, including setting the equality operator,
        threshold, and queue sources. Emits the finished signal when complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()

        self.set_agent_and_aux()
        self.set_equality_operator()
        self.set_user_list()

        self.finished.emit()

    def set_state_changed_to(self, state):

        state_dropdown_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_Arrow")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        state_dropdown_btn.click()

        agent_state_changed_to = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_DropDown")]/div/ul/li',
            state,
        )
        if not agent_state_changed_to:
            raise ValueError(
                f"For Action Trigger State - Cant not find {state}. Make sure the state text is correct"
            )

    def set_agent_aux(self, aux) -> None:
        """
        Sets the the aux code for the state changed to.

        Args:
            aux (str): the aux code.

        Returns:
            None: This function does not return a value.
        """
        aux_code_input = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateAuxCodeValue")]',
            WaitConditions.VISIBILITY,
            raise_exception=True,
        )

        aux_code_input.send_keys(aux)

    def set_agent_and_aux(self) -> None:
        """
        Sets the agent state and aux code for the state changed to for the array of state.

        Returns:
            None: This function does not return a value.
        """
        for agent_changed in self.action_based["details"]["state"]:
            self.set_state_changed_to(agent_changed["code"])
            self.set_agent_aux(agent_changed["aux"])

            agent_state_add_plus_button = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_divParameters")]/div[1]/div[1]/div[3]/img',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )
            agent_state_add_plus_button.click()

            sleep(1)

    def set_equality_operator(self) -> None:
        """
        Sets the the equality operator for the state changed to.

        Returns:
            None: This function does not return a value.
        """
        user_selected_equality_op = self.action_based["details"]["equality_operator"]

        self.logging(
            f"Setting equality operator to {user_selected_equality_op}.", "INFO"
        )
        if user_selected_equality_op == "Equal To":

            equal_button = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_ctl16_0")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )
            equal_button.click()
        elif user_selected_equality_op == "Not Equal To":

            not_equal_button = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_ctl16_1")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )
            not_equal_button.click()

    def set_user_list(self) -> None:
        """
        Sets the user list for the state changed to rule.

        Returns:
            None: This function does not return a value.
        """
        user_list_selection = self.action_based["details"]["user_list"]

        user_list_dropdown_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "user_filter_static_id_Arrow")]',
            WaitConditions.VISIBILITY,
            raise_exception=True,
        )
        user_list_dropdown_btn.click()

        agent_state_changed_to = self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "user_filter_static_id_DropDown")]/div/ul/li',
            user_list_selection,
        )
        if not agent_state_changed_to:
            raise ValueError(
                f"For Action Trigger State - Cant not find {user_list_selection}. Make sure the User List text is correct"
            )
