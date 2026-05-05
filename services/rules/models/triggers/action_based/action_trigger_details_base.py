from dataclasses import dataclass
from ....enums import ACTIONTRIGGERDETAILTYPE


@dataclass
class BaseActionTriggerDetails:
    action_type: ACTIONTRIGGERDETAILTYPE
