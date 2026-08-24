from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import QRESULTACTION, QRECOVERYACTION
from dataclasses import dataclass


@dataclass
class QueueResultDecision:
    action: QRESULTACTION
    recovery: QRECOVERYACTION
