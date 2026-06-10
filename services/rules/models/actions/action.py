from dataclasses import dataclass
from ...enums import ACTIONCATEGORY
from typing import TypeVar, Generic

ItemT = TypeVar("ItemT")


@dataclass
class Action(Generic[ItemT]):
    provider_category: ACTIONCATEGORY
    provider_instance: str
    provider_condition: str
    details: ItemT
