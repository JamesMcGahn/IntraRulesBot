from dataclasses import dataclass

from .condition_details_base import BaseConditionDetails
from ...enums import STATSEQUALITYOPERATOR, QUEUESSOURCE
from ...enums import CONDITIONDETAILTYPE


@dataclass
class ConditionStatsDetails(BaseConditionDetails):
    condition_type: CONDITIONDETAILTYPE
    equality_operator: STATSEQUALITYOPERATOR
    equality_threshold: int
    queues_source: QUEUESSOURCE
