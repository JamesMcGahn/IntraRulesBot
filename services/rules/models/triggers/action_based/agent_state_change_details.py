from dataclasses import dataclass, field


from .action_trigger_details_base import BaseActionTriggerDetails
from ....enums import STATEEQUALITYOPERATOR
from ...agent_state import AgentState


@dataclass
class AgentStateChangeDetails(BaseActionTriggerDetails):
    equality_operator: STATEEQUALITYOPERATOR
    state: list[AgentState] = field(default=list)
    user_list: str = "All Users"
