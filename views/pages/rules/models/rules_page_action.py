from dataclasses import dataclass
from typing import Generic, TypeVar

from ..enums.rules_page_event import RULESPAGEEVENT

T = TypeVar("T")


@dataclass(frozen=True)
class RulesPageAction(Generic[T]):
    event: RULESPAGEEVENT
    data: T
