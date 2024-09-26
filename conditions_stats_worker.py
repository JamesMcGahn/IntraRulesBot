from selenium.webdriver.common.by import By

from web_element_interactions import WaitConditions, WebElementInteractions
from worker_class import WorkerClass


class ConditionsStatsWorker(WorkerClass):
    def __init__(self, driver, conditions_worker, condition, index):
        super().__init__()
        self.driver = driver
        self.condition = condition
        self.index = index
        self.conditions_worker = conditions_worker
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"
        self.wELI.send_msg.connect(self.logging)

    def do_work(self):
        try:
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
        except Exception as e:
            self.logging(f"Something went wrong in ConditionsStatsWorker: {e}", "ERROR")
            raise Exception(e) from Exception

    def set_equality_operator(self, condition_details):
        self.logging(
            f"Selecting stats equality comparison operator for Condition {self.index+1}...",
            "INFO",
        )
        agents_in_after_call_eq_drop = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
            WaitConditions.CLICKABLE,
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

    def set_equality_threshold(self, condition_details):
        self.logging(
            f"Selecting stats threshold for Condition {self.index+1}...",
            "INFO",
        )
        agents_in_after_call_eq_condition = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_tbExposedDataValue")]',
            WaitConditions.VISIBILITY,
        )

        user_agents_in_after_call_eq_condition = condition_details["equality_threshold"]

        agents_in_after_call_eq_condition.send_keys(
            user_agents_in_after_call_eq_condition
        )

    def set_queues_sources_users(self):
        self.logging(
            f"Selecting queue source as 'users' for Condition {self.index+1}...",
            "INFO",
        )
        self.conditions_worker.rule_condition_queues_source = "users"

    def set_queues_sources_queue(self):
        self.logging(
            f"Selecting queue source as 'queues' for Condition {self.index+1}...",
            "INFO",
        )
        queues_radio_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl16_1")]',
            WaitConditions.CLICKABLE,
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
