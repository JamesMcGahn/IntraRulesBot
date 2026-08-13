from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderStatistics:
    key: str
    value: str
    odata_type: str
