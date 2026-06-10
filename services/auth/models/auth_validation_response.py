from dataclasses import dataclass
from ..enums import PROVIDERS


@dataclass
class AuthValidationResponse:
    provider: PROVIDERS
    cookies_valid: bool = False
    token_valid: bool = False
