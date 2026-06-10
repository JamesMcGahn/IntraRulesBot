from dataclasses import dataclass
from ...enums import CONDITIONCATEGORY
from typing import TypeVar, Generic

ItemT = TypeVar("ItemT")


@dataclass
class Condition(Generic[ItemT]):
    provider_category: CONDITIONCATEGORY
    provider_instance: str
    provider_condition: str
    details: ItemT
