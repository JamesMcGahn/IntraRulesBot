from enum import StrEnum


class RULESPAGEEVENT(StrEnum):
    DELETE_RULE = "delete_rule"
    DELETE_ALL_RULES = "delete_all_rules"
    CLONE_RULE = "clone_rule"
    VALIDATE_RULES = "validate_rules"
    USER_SAVE_RULES = "user_save_rules"
    SYS_SAVE_RULES = "sys_save_rules"
    BOOKMARK_RULES = "bookmark_rules"
    COPY_RULE_FIELD = "copy_rule_field"
    START_RUNNER = "start_runner"
    STOP_RUNNER = "stop_runner"
    TOGGLE_DISPLAY_MONITOR = "toggle_display_monitor"
