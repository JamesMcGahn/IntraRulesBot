from dataclasses import dataclass
from ....enums import ACTIONTRIGGERCATEGORY
from .action_trigger_details_base import BaseActionTriggerDetails


@dataclass
class ActionTrigger:
    provider_category: ACTIONTRIGGERCATEGORY
    provider_instance: str
    provider_condition: str
    details: BaseActionTriggerDetails
