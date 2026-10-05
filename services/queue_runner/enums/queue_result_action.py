from enum import StrEnum


class QRESULTACTION(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"
    RETRY = "retry"
    STOP = "stop"
    ABORT_RUN = "abort_run"
