from dataclasses import dataclass


@dataclass(frozen=True)
class SpreadSheetImport:
    file_location: str
    provider_name: str
    provider_instance: str
