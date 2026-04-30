from dataclasses import dataclass, field

from ....enums import ACTIONTRIGGERDETAILTYPE
from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import STATEEQUALITYOPERATOR
from ...agent_state import AgentState


@dataclass
class AgentStateChangeDetails(BaseActionTriggerDetails):
    equality_operator: STATEEQUALITYOPERATOR
    action_type: ACTIONTRIGGERDETAILTYPE = ACTIONTRIGGERDETAILTYPE.STATE
    state: list[AgentState] = field(default=list)
    user_list: str = "All Users"
