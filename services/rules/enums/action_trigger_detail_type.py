from enum import StrEnum


class ACTIONTRIGGERDETAILTYPE(StrEnum):
    STATE_CHANGED = "state_changed"
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    TIME_IN_STATE = "time_in_state"
    QUICK_ACTION = "quick_action"
