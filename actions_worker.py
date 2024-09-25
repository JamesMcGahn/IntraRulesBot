from time import sleep

from PySide6.QtCore import QObject
from selenium.webdriver.common.by import By

from actions_email_worker import ActionsEmailWorker
from web_element_interactions import WaitConditions, WebElementInteractions


class ActionsWorker(QObject):

    def __init__(self, driver, rule):
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"

    @property
    def rule_condition_queues_source(self):
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source):
        self._rule_condition_queues_source = source

    def do_work(self):
        for i, action in enumerate(self.rule["actions"]):

            self.set_provider_category(action)
            self.set_provider_instance(action)
            self.set_provider_condition(action)
            self.set_email_action(action, self.rule)
            self.add_additional_action(i)

    def set_provider_category(self, action):
        user_action_category_selection = action["provider_category"]

        action_category_dropdown = self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
            user_action_category_selection,
        )
        if not action_category_dropdown:
            print(
                f"Cant not find {action_category_dropdown}. Make sure the provider category for the action text is correct"
            )
            return
        sleep(3)

    def set_provider_instance(self, action):
        user_action_provider_instance = action["provider_instance"]

        action_provider_dropdown = self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuProviderInstance")]/ul/li',
            user_action_provider_instance,
        )
        if not action_provider_dropdown:
            print(
                f"Cant not find {user_action_provider_instance}. Make sure the action provider text is correct"
            )
            return

        sleep(3)

    def set_provider_condition(self, action):
        user_action_selection = action["provider_condition"]
        action_selection_dropdown = self.wELI.select_item_from_list(
            10,
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuItem")]/ul/li',
            user_action_selection,
        )
        if not action_selection_dropdown:
            print(
                f"Cant not find {user_action_selection}. Make sure the action provider text is correct"
            )
            return

    def set_email_action(self, action, rule):
        if action["details"]["action_type"] == "email":
            actions_worker = ActionsEmailWorker(self.driver, self, action, rule)
            actions_worker.do_work()

    def add_additional_action(self, i):
        if i != len(self.rule["actions"]) - 1 and len(self.rule["actions"]) > 1:
            add__addit_action = self.wELI.wait_for_element(
                15,
                By.XPATH,
                '//*[contains(@id, "overlayContent_lblAddAction")]',
                WaitConditions.CLICKABLE,
            )
            add__addit_action.click()
