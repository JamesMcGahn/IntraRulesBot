from dataclasses import dataclass, field


from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import STATEEQUALITYOPERATOR
from ...agent_state import AgentState
from ....enums import ACTIONTRIGGERDETAILTYPE


@dataclass
class AgentTimeInStateDetails(BaseActionTriggerDetails):
    action_type: ACTIONTRIGGERDETAILTYPE
    equality_operator: STATEEQUALITYOPERATOR
    aux_equality_operator: STATEEQUALITYOPERATOR
    equality_threshold: int
    state: list[AgentState] = field(default_factory=list)
    user_list: str = "All Users"
