from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..profiles.models import BrowserProfile
    from services.logger.adapters import LogAdapter

from base.enums import INTRAVERSION
from .defaults.profile_v_10 import v_10
from .defaults.profile_v_11 import v_11
from base import ServiceBase


class ProfileRegistry(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger=logger)
        self._default_profiles = {INTRAVERSION.V10: v_10, INTRAVERSION.V11: v_11}
        self._registry = {INTRAVERSION.V10: v_10, INTRAVERSION.V11: v_11}

    def get_profile(self, version: INTRAVERSION) -> BrowserProfile:
        profile = self._registry.get(version, None)
        if profile is None:
            raise NotImplementedError(f"version {version} has not been implemented")
        return profile

    def set_profile_to_default(self, version: INTRAVERSION):
        if not isinstance(version, INTRAVERSION):
            raise TypeError(
                f"Type must be of INTRAVERSION. Type passed: {type(version)}"
            )
        self._registry[version] = self._default_profiles.get(version)
        self._logging(f"Successfully set Browser Profile - {version} to default.")

    def set_profile(self, profile: BrowserProfile):
        self._registry[profile.version] = profile
        self._logging(f"Successfully set Browser Profile - {profile.version}.")
