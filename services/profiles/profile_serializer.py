from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import BrowserProfile
    from services.logger.adapters import LogAdapter


from dataclasses import asdict

from enum import Enum

from base import ServiceBase


class ProfileSerializer(ServiceBase):
    def __init__(self, logger: LogAdapter):
        super().__init__(logger=logger)

    def to_schema_dict(self, profile: BrowserProfile) -> dict:
        schema_dict = {
            "schema_version": 1,
            "version": profile.version,
            "selectors": self.normalize(asdict(profile.selectors)),
        }
        return schema_dict

    def normalize(self, obj):
        if isinstance(obj, Enum):
            return obj.value

        if isinstance(obj, list):
            return [self.normalize(x) for x in obj]

        if isinstance(obj, dict):
            return {self.normalize(k): self.normalize(v) for k, v in obj.items()}

        return obj
