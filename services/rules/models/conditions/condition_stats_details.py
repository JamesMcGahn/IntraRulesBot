from dataclasses import dataclass

from ...enums import CONDITIONDETAILTYPE
from .condition_details_base import BaseConditionDetails
from ...enums import STATSEQUALITYOPERATOR, QUEUESSOURCE


@dataclass
class ConditionStatsDetails(BaseConditionDetails):
    equality_operator: STATSEQUALITYOPERATOR
    equality_threshold: int
    queues_source: QUEUESSOURCE
    condition_type: CONDITIONDETAILTYPE = CONDITIONDETAILTYPE.STATS
