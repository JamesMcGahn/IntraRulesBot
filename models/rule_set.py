from typing import List

from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from rule_sets import rule_set_list
from services.settings import AppSettings


class RuleSetsModel(QObject, metaclass=QSingleton):
    """
    Manages the rule set data for the application, allowing for adding, saving, and resetting
    rules. It interacts with persistent storage through AppSettings and emits signals when
    the data changes.

    Attributes:
        _rule_sets (list): Internal list storing the rule set data.
        settings (AppSettings): The application settings instance for saving and loading rules.

    Signals:
        data_changed (Signal): Emitted when user rule sets are added.
        success (Signal): Emitted after a successful operation, such as saving rule set.
    """

    data_changed = Signal(list)
    success = Signal()

    def __init__(self):
        """
        Initializes the RulesModel with an empty list of rules and loads saved rules
        from persistent storage.
        """
        super().__init__()
        self._rule_sets = []
        self._user_rule_sets = []
        self._default_rule_sets = []
        self.settings = AppSettings()
        self.init_rule_set_model()

    @property
    def rule_sets(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return self._rule_sets

    @Slot(object)
    def add_rule_set(self, rule_set: object) -> None:
        """
        Adds a single rule to the model and emits the data_changed signal.

        Args:
            rule (object): The rule to be added.

        Returns:
            None: This function does not return a value.
        """
        self._user_rule_sets.append(rule_set)
        self.save_rule_sets()
        self.data_changed.emit(rule_set)

    @Slot(str)
    def delete_rule_set(self, id: str) -> None:
        """
        Delete the rule set from user rule sets

        Args:
            id (str): The id of the rule set

        Returns:
            None: This function does not return a value.
        """
        if id:
            rule_sets = [
                rule_set for rule_set in self._user_rule_sets if rule_set.id != id
            ]
            self._user_rule_sets = rule_sets
            self.save_rule_sets()

    @Slot()
    def reset_model(self) -> None:
        """
        Resets the model by clearing all user rule sets and updating the persistent storage.
        Emits the data_changed signal after the reset.

        Returns:
            None: This function does not return a value.
        """
        self.settings.begin_group("rule-set-model")
        self.settings.set_value("rule-sets_saved", [])
        self.settings.end_group()
        self._user_rule_sets = []
        self._rule_sets = rule_set_list
        self.data_changed.emit(self._rule_sets)

    @Slot(list)
    def save_rule_sets(self) -> None:
        """
        Saves the provided rule sets to persistent storage.

        Returns:
            None: This function does not return a value.
        """
        self.settings.begin_group("rule-set-model")
        self.settings.set_value("rule-sets_saved", self._user_rule_sets)
        self.settings.end_group()

    def init_rule_set_model(self) -> None:
        """
        Initializes the rule set model by loading saved user rule sets from persistent storage.
        It loads default rule sets from the rule_sets module.
        If no rules are found, an empty list is used for user rule sets.
        Default rule sets are combined with user rule sets.
        """
        self.settings.begin_group("rule-set-model")
        self._user_rule_sets = self.settings.get_value("rule-sets_saved", [])
        self.settings.end_group()
        self._rule_sets = rule_set_list + self._user_rule_sets
