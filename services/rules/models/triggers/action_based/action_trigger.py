from dataclasses import dataclass
from ....enums import ACTIONTRIGGERCATEGORY
from typing import TypeVar, Generic

ItemT = TypeVar("ItemT")


@dataclass
class ActionTrigger(Generic[ItemT]):
    provider_category: ACTIONTRIGGERCATEGORY
    provider_instance: str
    provider_condition: str
    details: ItemT
