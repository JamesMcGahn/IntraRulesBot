from enum import StrEnum


class EXECUTORTASK(StrEnum):
    OPEN_FORM = "open_form"
    SET_RULE_NAME = "set_rule_name"
    EXECUTE_TRIGGERS = "execute_triggers"
    EXECUTE_CONDITIONS = "execute_conditions"
    EXECUTE_ACTIONS = "execute_actions"
    SET_RULE_CATEGORY = "set_rule_category"
    SUBMIT_RULE = "submit_rule"

    # shared child level tasks
    SET_CATEGORY = "set_category"
    SET_INSTANCE = "set_instance"
    SET_TYPE = "set_type"
    SET_ITEM = "set_item"
    DETAIL = "detail"
    ADD_NEXT = "add_next"
