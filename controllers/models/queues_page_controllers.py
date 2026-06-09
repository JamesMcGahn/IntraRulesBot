from dataclasses import dataclass

from ..queues.queues_controller import QueuesController
from ..queues.queues_run_monitor_controller import QueuesRunMonitorController


@dataclass
class QueuesPageControllers:
    queues: QueuesController
    monitor: QueuesRunMonitorController
