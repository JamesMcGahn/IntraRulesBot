from enum import StrEnum


class QUEUESPAGEEVENT(StrEnum):
    START_RUNNER = "start_runner"
    STOP_RUNNER = "stop_runner"
    TOGGLE_DISPLAY_MONITOR = "toggle_display_monitor"
