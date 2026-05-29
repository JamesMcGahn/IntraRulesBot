from dataclasses import dataclass


@dataclass
class ProviderSessionData:
    cookies: list[dict]
    token: str | None
