from dataclasses import dataclass, field
from .queue_run_item import QueueRunItem
from .queue_run_config import QueueRunnerConfig


@dataclass
class QueueRunnerRequestPayload:
    config: QueueRunnerConfig
    provider_name: str
    provider_instance: str
    queues: list[QueueRunItem] = field(default_factory=list)
