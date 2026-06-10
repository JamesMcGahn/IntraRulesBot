from dataclasses import dataclass
from ...enums import CONDITIONDETAILTYPE


@dataclass
class BaseConditionDetails:
    condition_type: CONDITIONDETAILTYPE
