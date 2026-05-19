from dataclasses import dataclass
from ...enums import ACTIONDETAILTYPE
from .action_details_base import BaseActionDetails


@dataclass
class ActionsEmailDetails(BaseActionDetails):
    action_type: ACTIONDETAILTYPE
    email_subject: str
    email_body: str
    email_address: str
