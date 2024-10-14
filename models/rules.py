from typing import List

from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from services.settings import AppSettings


class RulesModel(QObject, metaclass=QSingleton):
    """
    Manages the rules data for the application, allowing for adding, saving, and resetting
    rules. It interacts with persistent storage through AppSettings and emits signals when
    the data changes.

    Attributes:
        _rules (list): Internal list storing the rules data.
        settings (AppSettings): The application settings instance for saving and loading rules.

    Signals:
        data_changed (Signal): Emitted when rules are modified.
        success (Signal): Emitted after a successful operation, such as saving rules.
    """

    data_changed = Signal(list)
    success = Signal()

    def __init__(self):
        """
        Initializes the RulesModel with an empty list of rules and loads saved rules
        from persistent storage.
        """
        super().__init__()
        self._rules = []
        self.settings = AppSettings()
        self.init_rules_model()

    @property
    def rules(self) -> List:
        """
        Property to access the list of rules.

        Returns:
            list: The list of current rules.
        """
        return self._rules

    @Slot(object)
    def add_rule(self, rule: object) -> None:
        """
        Adds a single rule to the model and emits the data_changed signal.

        Args:
            rule (object): The rule to be added.

        Returns:
            None: This function does not return a value.
        """
        self._rules.append(rule)
        self.data_changed.emit(rule)

    @Slot(list)
    def add_rules(self, rules: List) -> None:
        """
        Adds multiple rules to the model and emits the data_changed signal.

        Args:
            rules (list): A list of rules to be added.

        Returns:
            None: This function does not return a value.
        """
        self._rules.append([rule for rule in rules])
        self.data_changed.emit(rules)

    @Slot()
    def reset_model(self) -> None:
        """
        Resets the model by clearing all rules and updating the persistent storage.
        Emits the data_changed signal after the reset.

        Returns:
            None: This function does not return a value.
        """
        self.settings.begin_group("rules-model")
        self.settings.set_value("rules_saved", [])
        self.settings.end_group()
        self._rules = []
        self.data_changed.emit(self._rules)

    @Slot(list)
    def save_rules(self, rules) -> None:
        """
        Saves the provided rules to persistent storage and updates the internal state.

        Args:
            rules (list): A list of rules to be saved.

        Returns:
            None: This function does not return a value.
        """
        self.settings.begin_group("rules-model")
        self.settings.set_value("rules_saved", rules)
        self._rules = rules
        self.settings.end_group()

    def init_rules_model(self) -> None:
        """
        Initializes the rules model by loading saved rules from persistent storage.
        If no rules are found, an empty list is used.
        """
        self.settings.begin_group("rules-model")
        self._rules = self.settings.get_value("rules_saved", [])
        self.settings.end_group()
