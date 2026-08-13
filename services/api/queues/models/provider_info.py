from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderInfo:
    id: str
    name: str
    provider_type: str
    manage_queue_id: str | None
