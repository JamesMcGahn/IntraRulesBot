from dataclasses import dataclass, field

from .condition_details_base import BaseConditionDetails
from ...enums import (
    CONDITIONDETAILTYPE,
    STATEEQUALITYOPERATOR,
    SEGMENTTIMEINTERVAL,
    SEGMENTSTARTTIME,
    MATCHMODE,
)


@dataclass
class ConditionWFMSegmentCodesDetails(BaseConditionDetails):
    condition_type: CONDITIONDETAILTYPE
    equality_operator: STATEEQUALITYOPERATOR
    match_mode: MATCHMODE
    segment_time_interval: SEGMENTTIMEINTERVAL
    segment_start_time: SEGMENTSTARTTIME
    segment_occurrence: str

    segment_codes: list = field(default_factory=list)

    segment_offset: int | None = None
    segment_end_time: str | None = None
    segment_duration: int | None = None

    user_list: str = "All Users"
