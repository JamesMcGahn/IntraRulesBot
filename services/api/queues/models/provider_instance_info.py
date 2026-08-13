from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.queues.models import Queue

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProviderInstanceInfo:
    id: str
    name: str
    queues: Queue = field(default_factory=list)
