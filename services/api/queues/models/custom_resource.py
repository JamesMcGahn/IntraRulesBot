from dataclasses import dataclass


@dataclass(frozen=True)
class CustomResource:
    id: str
    name: str
    providerDefinitionId: str
