from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.settings.models import LogSettings
    from base.events import UIEvent

from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from base.enums import LOGLEVEL, UIEVENTTYPE

# from components.toasts.qtoast.enums import QTOASTSTATUS
from services.settings.enums import FIELDSTATESTATUS, SETTINGSCATEGORIES
from services.settings.events import FieldStateEvent
from services.settings.models import LogSettings
from views.components.toasts.qtoast.enums import QTOASTSTATUS
from .tab_settings_ui import TabSettingsBaseUI
from .tab_ui_helper import SettingsUIHelper


class TabSettingsBase(QWidgetBase):
    settings_field_updated = Signal(str, str, object)
    send_to_verify = Signal(str, str, str)
    send_batch_to_verify = Signal(object)
    verify_response_update = Signal(str, str, bool)
    change_verify_btn_disable = Signal(str, str, bool)

    def __init__(
        self,
        tab_id: SETTINGSCATEGORIES,
        settings: LogSettings,
        settings_verify,
        field_registry,
    ):
        super().__init__()
        self.tab_id = tab_id
        self.field_registry = field_registry
        self.sui = SettingsUIHelper(settings_verify, field_registry)
        self.view = TabSettingsBaseUI(self.tab_id, settings, self.sui)
        self.layout.addWidget(self.view)

        # SIGNAL CONNECTIONS
        self.sui.send_to_verify.connect(self.send_to_verify)
        self.sui.send_batch_to_verify.connect(self.send_batch_to_verify)
        self.verify_response_update.connect(self.sui.verify_response_update)
        self.sui.settings_field_updated.connect(self.settings_field_updated)

    @Slot(object)
    def on_verify_response(self, event: UIEvent):
        if event.event_type == UIEVENTTYPE.UPDATE and isinstance(
            event.payload, FieldStateEvent
        ):
            if event.payload.category == self.tab_id:
                tab = event.payload.category
                field = event.payload.field
                status = event.payload.status
                if status == FIELDSTATESTATUS.VALID:
                    self.change_verify_btn_disable.emit(tab, field, False)
                elif status == FIELDSTATESTATUS.INVALID:
                    is_valid = False
                    self.change_verify_btn_disable.emit(tab, field, False)
                elif status == FIELDSTATESTATUS.LOADING:
                    is_valid = False
                    self.verify_response_update.emit(tab, field, is_valid)
