from dataclasses import dataclass, field


from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import ACTIONTRIGGERDETAILTYPE, LOOKUPOPERATOR, SEGMENTLOOKUP


@dataclass
class SegmentOccurrenceDetails(BaseActionTriggerDetails):
    action_type: ACTIONTRIGGERDETAILTYPE
    lookup_operator: LOOKUPOPERATOR
    segment_lookup: SEGMENTLOOKUP
    segment_codes: list = field(default_factory=list)
    lead_time: int = 5
    user_list: str = "All Users"
