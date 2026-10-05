from enum import StrEnum


class QUEUEEXECSTATUS(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    BROWSER_ERROR = "browser_error"
    NAME_EXISTS_ERROR = "name_exists_error"
    UNKNOWN_ERROR = "unknown_error"
    RUNNER_STOPPED_ERROR = "runner_stopped_error"
    TIMEOUT_ERROR = "timeout_error"
    QUEUE_NOT_FOUND_ERROR = "not_found_error"
    QUEUE_FOUND_ERROR = "queue_found_error"
    NOT_AUTHENTICATED = "not_authenticated"
    NETWORK_RESPONSE_ERROR = "network_response_error"
    NETWORK_RETRYABLE_ERROR = "network_retryable_error"
    FATAL_ERROR = "fatal_error"
