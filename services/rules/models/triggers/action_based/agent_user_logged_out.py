from dataclasses import dataclass


from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import ACTIONTRIGGERDETAILTYPE


@dataclass
class AgentLoggedOutDetails(BaseActionTriggerDetails):
    action_type: ACTIONTRIGGERDETAILTYPE
    user_list: str = "All Users"
