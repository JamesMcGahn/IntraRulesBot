from dataclasses import dataclass

from ..queues.queues_controller import QueuesController


@dataclass
class QueuesPageControllers:
    queues: QueuesController
