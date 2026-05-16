from enum import StrEnum


class EXECUTORSCOPE(StrEnum):
    RULE = "rule"
    TRIGGER = "trigger"
    CONDITION = "condition"
    ACTION = "action"
