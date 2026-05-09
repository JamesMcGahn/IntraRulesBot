from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rule_sets import RuleSetRegistry, RuleSetStore, RuleSetSerializer
    from services.rule_sets import RuleSetBuilder
    from services.rule_sets.models import RuleSet
    from services.rules import RuleSerializer
from PySide6.QtCore import Signal, Slot
from base import QObjectBase
from utils.files import PathManager
from pathlib import Path
from base.enums import UIEVENTTYPE, LOGLEVEL
from base.events import ToastEvent, UIEvent, SchemaErrorDialogEvent, RuleSetsLoadedEvent
from views.components.toasts.qtoast.enums import QTOASTSTATUS


class RuleSetsController(QObjectBase):
    ui_event = Signal(object)

    def __init__(
        self,
        rules_set_registry: RuleSetRegistry,
        rule_set_builder: RuleSetBuilder,
        rule_set_store: RuleSetStore,
        rule_set_serializer: RuleSetSerializer,
    ):
        super().__init__()
        self.rule_set_registry = rules_set_registry
        self.rule_set_builder = rule_set_builder
        self.rule_set_store = rule_set_store
        self.rule_serializer = rule_set_serializer

    def hydrate_rule_set_page(self):
        self._emit_rule_sets_updated()

    def load_editor_state(self):
        path = PathManager.create_folder_in_app_data("user_rule_sets")
        files = [f for f in Path(path).iterdir() if f.is_file()]
        raw_rulesets = []
        for file in files:
            raw, message = self.rule_set_store.load_from_json(file)
            if raw is None:
                continue
            raw_rulesets.append(raw)
        raw_rulesets.extend(self.rule_set_store.load_from_internal())

        built_rule_sets = self.rule_set_builder.build_rule_sets(raw_rulesets)
        self.rule_set_registry.add_rule_sets(built_rule_sets)

    def _emit_rule_sets_updated(self):
        self.ui_event.emit(
            UIEvent(
                event_type=UIEVENTTYPE.DISPLAY,
                payload=RuleSetsLoadedEvent(rule_sets=self.rule_set_registry.get_all()),
            )
        )

    def rule_set_edited(self, rule_set: RuleSet):
        can_edit = not rule_set.default
        message = f"{rule_set.rule_set_name}: " + (
            "Rule Set Updated." if can_edit else "Default Rule Sets can't be updated."
        )
        title = "Rule Set Updated" if can_edit else "Default Rule Sets Can't Be Editted"
        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=QTOASTSTATUS.SUCCESS,
            log_level=LOGLEVEL.INFO,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)
        if not can_edit:
            return
        self.rule_set_registry.upsert(rule_set)
        self._emit_rule_sets_updated()

    def rule_set_to_file(self, guid: str, file_path: str):
        rule_set = self.rule_set_registry.get(guid)
        dict_rule_set = self.rule_serializer.to_schema_dict(rule_set)
        self.rule_set_store.save(dict_rule_set, file_path)
