from enum import StrEnum


class RULEEXECSTATUS(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    BROWSER_ERROR = "browser_error"
    NAME_EXISTS_ERROR = "name_exists_error"
    UNKNOWN_ERROR = "unknown_error"
    RUNNER_STOPPED_ERROR = "runner_stopped_error"
    TIMEOUT_ERROR = "timeout_error"
