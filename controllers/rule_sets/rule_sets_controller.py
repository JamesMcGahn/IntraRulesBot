from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rule_sets import (
        RuleSetRegistry,
        RuleSetSerializer,
        DefaultRuleSetProvider,
    )
    from services.rule_sets import RuleSetBuilder
    from services.rule_sets.models import RuleSet
    from services.files import JSONFileService
    from services.logger.adapters import LogAdapter


from PySide6.QtCore import Signal
from utils.files import PathManager
from pathlib import Path
from base.enums import UIEVENTTYPE, LOGLEVEL
from base.events import ToastEvent, UIEvent, RuleSetsLoadedEvent
from views.components.toasts.qtoast.enums import QTOASTSTATUS
from base import ControllerBase


class RuleSetsController(ControllerBase):
    load_rule_set_from_bookmark = Signal(object)

    def __init__(
        self,
        logger: LogAdapter,
        rules_set_registry: RuleSetRegistry,
        rule_set_builder: RuleSetBuilder,
        json_file_service: JSONFileService,
        rule_set_serializer: RuleSetSerializer,
        default_rule_set_provider: DefaultRuleSetProvider,
    ):
        super().__init__(logger)
        self.rule_set_registry = rules_set_registry
        self.rule_set_builder = rule_set_builder
        self.json_file_service = json_file_service
        self.rule_serializer = rule_set_serializer
        self.default_provider = default_rule_set_provider

    def hydrate_rule_set_page(self):
        self._emit_rule_sets_updated()

    def load_editor_state(self):
        path = PathManager.create_folder_in_app_data("user_rule_sets")
        files = [f for f in Path(path).iterdir() if f.is_file()]
        raw_rulesets = []
        for file in files:
            res = self.json_file_service.load(file)
            if not res.ok or res.data is None:
                continue
            raw_rulesets.append(res.data)
        raw_rulesets.extend(self.default_provider.load())

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

    # TODO TOASTs
    def rule_set_to_file(self, guid: str, file_path: str):
        rule_set = self.rule_set_registry.get(guid)
        dict_rule_set = self.rule_serializer.to_schema_dict(rule_set)
        self.json_file_service.save(dict_rule_set, file_path)

    # TODO TOASTs
    def rule_set_delete(self, rule_set: RuleSet):

        if rule_set.default:
            title = "Cannot Delete Ruleset"
            message = "Default Rule Sets cannot be deleted."
            level = QTOASTSTATUS.INFORMATION

        else:
            self.rule_set_registry.delete(rule_set.guid)
            title = "Ruleset Deleted"
            message = f"Rule Set: {rule_set.rule_set_name} successfully deleted."
            level = QTOASTSTATUS.INFORMATION
            self._emit_rule_sets_updated()

        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=level,
            log_level=LOGLEVEL.INFO,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)

    def rule_set_added(self, rule_set: dict):
        built_rule_set = self.rule_set_builder.build_rule_set(rule_set)
        path = PathManager.create_folder_in_app_data("user_rule_sets")
        file_path = Path(path) / f"{built_rule_set.guid}.json"
        self.json_file_service.save(rule_set, file_path)
        self.rule_set_registry.add_rule_sets([built_rule_set])
        self._emit_rule_sets_updated()

    def load_to_editor(self, guid: str):
        rule_set = self.rule_set_registry.get(guid)
        self.load_rule_set_from_bookmark.emit(rule_set)
