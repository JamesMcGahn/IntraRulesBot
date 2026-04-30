from dataclasses import dataclass
from ...enums import ACTIONCATEGORY
from .action_details_base import BaseActionDetails


@dataclass
class Action:
    provider_category: ACTIONCATEGORY
    provider_instance: str
    provider_condition: str
    details: BaseActionDetails
