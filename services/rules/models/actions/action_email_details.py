from dataclasses import dataclass

from .action_details_base import BaseActionDetails
from ...enums import ACTIONDETAILTYPE


@dataclass
class ActionsEmailDetails(BaseActionDetails):
    email_subject: str
    email_body: str
    email_address: str
    action_type: ACTIONDETAILTYPE = ACTIONDETAILTYPE.EMAIL
