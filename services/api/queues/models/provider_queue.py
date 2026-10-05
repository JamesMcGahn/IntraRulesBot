from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderQueue:
    queue_name: str
    queue_number: str
    queue_id: str
    odata_type: str
