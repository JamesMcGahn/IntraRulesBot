from dataclasses import dataclass

from base.enums import LOGLEVEL
from views.components.toasts.qtoast.enums import QTOASTSTATUS


@dataclass
class ToastEvent:
    message: str
    title: str
    toast_level: QTOASTSTATUS
    log_level: LOGLEVEL
