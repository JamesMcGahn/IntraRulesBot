from enum import StrEnum


class QEXECUTORTASK(StrEnum):
    START = "start"
    ENSURE_FORM_OPEN = "ensure_form_open"
    FIND_PROVIDER_NAME = "find_provider"
    OPEN_PROVIDER_FORM = "open_provider_form"
    FIND_PROVIDER_INSTANCE = "set_instance"
    SWITCH_TO_INSTANCE_CONFIG = "switch_to_instance_config"
    OPEN_QUEUE_FORM = "open_queue_form"
    SET_QUEUE_NAME = "set_queue_name"
    SET_QUEUE_NUMBER = "set_queue_number"
    SUBMIT_QUEUE = "submit_queue"
    VERIFY_SUBMISSION = "verify_submission"
