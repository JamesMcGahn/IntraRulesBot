from enum import StrEnum


class QUEUERUNSTATUS(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"
