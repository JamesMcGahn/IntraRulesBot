from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...services.queue_runner.enums import QUEUERUNNERLIFECYCLE

from dataclasses import dataclass


@dataclass
class QueueRunnerStateEvent:
    state: QUEUERUNNERLIFECYCLE
