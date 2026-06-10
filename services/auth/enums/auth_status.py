from enum import StrEnum


class AUTHSTATUS(StrEnum):
    SUCCESS = "success"
    ALREADY_AUTHENTICATED = "already_authenticated"
    INVALID_CREDENTIALS = "invalid_credentials"
    COOLDOWN = "cooldown"
    BROWSER_ERROR = "browser_error"
    UNKNOWN_ERROR = "unknown_error"
    STOPPED_REQUESTED = "stopped_requested"
    DUPLICATE_SESSION = "duplicate_session"
