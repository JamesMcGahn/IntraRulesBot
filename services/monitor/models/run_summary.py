from dataclasses import dataclass


@dataclass()
class RunSummary:
    total: int = 0
    completed: int = 0
    succeeded: int = 0
    failed: int = 0
    retrying: int = 0
    stopped: int = 0
    pending: int = 0
