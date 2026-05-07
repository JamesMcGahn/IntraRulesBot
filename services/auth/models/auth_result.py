from dataclasses import dataclass
from ..enums.auth_status import AUTHSTATUS


@dataclass
class AuthResult:
    success: bool
    status: AUTHSTATUS
    message: str = ""
