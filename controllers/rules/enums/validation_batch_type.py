from enum import StrEnum


class VALIDATIONBATCHTYPE(StrEnum):
    RUNTIME = "runtime"
    IMPORT = "import"
    USER_SAVE = "user_save"
    SYS_SAVE = "sys_save"
    RULE_RUNNER = "rule_runner"
    BOOKMARK = "bookmark"
