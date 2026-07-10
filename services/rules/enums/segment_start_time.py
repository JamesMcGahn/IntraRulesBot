from enum import StrEnum


class SEGMENTSTARTTIME(StrEnum):
    RULE_RUNTIME = "Rule Runtime"
    RULE_RUN_MINUS = "Rule Runtime Minus"
    RULE_RUN_PLUS = "Rule Runtime Plus"
    SHIFT_START = "Shift Start Time"
    VTO_REQ_START = "VTO Request Start Time"
