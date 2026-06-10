from dataclasses import dataclass, field


from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import STATEEQUALITYOPERATOR
from ...agent_state import AgentState
from ....enums import ACTIONTRIGGERDETAILTYPE


@dataclass
class AgentStateChangeDetails(BaseActionTriggerDetails):
    action_type: ACTIONTRIGGERDETAILTYPE
    equality_operator: STATEEQUALITYOPERATOR
    state: list[AgentState] = field(default_factory=list)
    user_list: str = "All Users"
