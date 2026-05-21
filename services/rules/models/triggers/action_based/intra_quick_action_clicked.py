from dataclasses import dataclass


from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import ACTIONTRIGGERDETAILTYPE


@dataclass
class IntraQuickActionClicked(BaseActionTriggerDetails):
    action_type: ACTIONTRIGGERDETAILTYPE
    quick_action_name: str
