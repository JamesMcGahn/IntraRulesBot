from base.enums import INTRAVERSION
from .defaults.profile_v_10 import v_10


class ProfileRegistry:

    def __init__(self):

        self._registry = {INTRAVERSION.V10: v_10}

    def get_profile(self, version: INTRAVERSION):
        profile = self._registry.get(version, None)
        if profile is None:
            raise NotImplementedError(f"version {version} has not been implemented")
        return profile
