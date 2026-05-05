from dataclasses import dataclass

from .action_details_base import BaseActionDetails


@dataclass
class ActionsEmailDetails(BaseActionDetails):
    email_subject: str
    email_body: str
    email_address: str
