from enum import StrEnum


class EXECUTORTASK(StrEnum):
    START = "start"
    OPEN_FORM = "open_form"
    SET_RULE_NAME = "set_rule_name"
    EXECUTE_TRIGGERS = "execute_triggers"
    EXECUTE_CONDITIONS = "execute_conditions"
    EXECUTE_ACTIONS = "execute_actions"
    SET_RULE_CATEGORY = "set_rule_category"
    SUBMIT_RULE = "submit_rule"

    # shared child level tasks
    SET_PROVIDER_CATEGORY = "set_category"
    SET_PROVIDER_INSTANCE = "set_instance"
    SET_PROVIDER_CONDITION = "set_condition"
    EXECUTE_DETAIL = "detail"
    ADD_NEXT_ITEM = "add_next_item"
