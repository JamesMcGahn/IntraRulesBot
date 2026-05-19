from dataclasses import dataclass
from base.enums import INTRAVERSION
from ...profiles.rules.models import RuleExecutorSelectors


@dataclass(frozen=True)
class RulePathProfile:
    version: INTRAVERSION
    selectors: RuleExecutorSelectors
    # form_opener: RuleFormOpener
