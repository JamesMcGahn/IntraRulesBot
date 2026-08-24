from enum import StrEnum


class QRECOVERYACTION(StrEnum):
    NONE = "none"
    AUTHENTICATE = "authenticate"
    REBUILD_BROWSER = "rebuild_browser"
