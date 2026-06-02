from enum import StrEnum


class QEXECUTORTASK(StrEnum):
    START = "start"
    FIND_PROVIDER_NAME = "find_provider"
    FIND_PROVIDER_INSTANCE = "set_instance"
    OPEN_FORM = "open_form"
    SET_QUEUE_NAME = "set_queue_name"
    SUBMIT_QUEUE = "submit_rule"
