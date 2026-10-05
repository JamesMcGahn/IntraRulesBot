from dataclasses import dataclass


@dataclass
class TokenData:
    tenant: str
    refresh_token: str
    access_token: str
