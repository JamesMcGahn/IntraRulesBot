from dataclasses import dataclass
from ...enums import CONDITIONCATEGORY
from .condition_details_base import BaseConditionDetails


@dataclass
class Condition:
    provider_category: CONDITIONCATEGORY
    provider_instance: str
    provider_condition: str
    details: BaseConditionDetails
