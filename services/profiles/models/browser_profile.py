from dataclasses import dataclass
from base.enums import INTRAVERSION
from .executor_selectors import ExecutorSelectors


@dataclass(frozen=True)
class BrowserProfile:
    version: INTRAVERSION
    selectors: ExecutorSelectors
    # form_opener: RuleFormOpener
