from base import QWidgetBase
from models import RuleSetsModel, RulesModel

from .bookmarks_page_css import STYLES
from .bookmarks_page_ui import BookMarksPageView


class BookMarksPage(QWidgetBase):
    """
    A controller class for managing the BookMarks page, which allows users to load and view default rulesets or rulesets they saved.
    Attributes:
        ui (BookMarksPageView): The view class responsible for displaying the logs.
        layout (QVBoxLayout): The layout containing the UI components for the logs page.
    """

    def __init__(self):
        super().__init__()

        self.setStyleSheet(STYLES)
        # Initialize the UI for the LogsPage
        self.ui = BookMarksPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.rule_sets = RuleSetsModel()
        self.rules_model = RulesModel()

        # Slots / Signals
        self.rule_sets.rule_set_added.connect(self.ui.add_rule_set)
        self.ui.load_rules.connect(self.rules_model.add_rules)
        self.ui.delete_rule_set.connect(self.rule_sets.delete_rule_set)
        self.ui.init_rule_set(self.rule_sets.rule_sets)
        self.ui.edit_rule_set.connect(self.rule_sets.update_rule_set)
