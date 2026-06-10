from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..profiles.models import BrowserProfile

from base.enums import INTRAVERSION
from .defaults.profile_v_10 import v_10


class ProfileRegistry:

    def __init__(self):

        self._registry = {INTRAVERSION.V10: v_10}

    def get_profile(self, version: INTRAVERSION) -> BrowserProfile:
        profile = self._registry.get(version, None)
        if profile is None:
            raise NotImplementedError(f"version {version} has not been implemented")
        return profile
