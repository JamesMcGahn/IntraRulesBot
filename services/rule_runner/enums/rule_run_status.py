from enum import StrEnum


class RULERUNSTATUS(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"
