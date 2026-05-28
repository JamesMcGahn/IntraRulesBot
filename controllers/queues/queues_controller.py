from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from PySide6.QtCore import Signal
from base import QObjectBase
from utils.files import PathManager
from pathlib import Path
from base.enums import UIEVENTTYPE, LOGLEVEL
from base.events import ToastEvent, UIEvent, RuleSetsLoadedEvent
from views.components.toasts.qtoast.enums import QTOASTSTATUS


class QueuesController(QObjectBase):
    ui_event = Signal(object)
    load_rule_set_from_bookmark = Signal(object)

    def __init__(self):
        super().__init__()
