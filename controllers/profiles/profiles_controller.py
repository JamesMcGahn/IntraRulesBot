from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.profiles import ProfileSerializer, ProfileRegistry, ProfileBuilder
    from services.logger.adapters import LogAdapter
    from services.files import JSONFileService


from base import ControllerBase
from base.enums import INTRAVERSION
from utils.files import PathManager
from pathlib import Path


class ProfilesController(ControllerBase):

    def __init__(
        self,
        log_adapter: LogAdapter,
        profile_serializer: ProfileSerializer,
        profile_registry: ProfileRegistry,
        json_file_service: JSONFileService,
        profile_builder: ProfileBuilder,
    ):
        super().__init__(log_adapter)
        self.profile_serializer = profile_serializer
        self.profile_registry = profile_registry
        self.json_file_service = json_file_service
        self.profile_builder = profile_builder

        self.v10_file_name = "v10_profile.json"
        self.v11_file_name = "v11_profile.json"

    def save_profiles(self):
        v10 = self.profile_serializer.to_schema_dict(
            self.profile_registry.get_profile(INTRAVERSION.V10)
        )
        v11 = self.profile_serializer.to_schema_dict(
            self.profile_registry.get_profile(INTRAVERSION.V11)
        )

        path = PathManager.create_folder_in_app_data("profiles")
        v10_file_path = Path(path) / self.v10_file_name
        v11_file_path = Path(path) / self.v11_file_name

        self.json_file_service.save(v10, v10_file_path)
        self.json_file_service.save(v11, v11_file_path)

    def load_profiles(self):
        self.load_v10()
        self.load_v11()

    def load_v10(self):
        path = PathManager.create_folder_in_app_data("profiles")
        v10_file_path = Path(path) / self.v10_file_name
        v10_res = self.json_file_service.load(v10_file_path)
        problem_path = v10_file_path.with_name("problem_v10_profile.json")

        if not v10_res.ok or v10_res.data is None:
            self.profile_registry.set_profile_to_default(INTRAVERSION.V10)
            if PathManager.path_exists(v10_file_path, False):
                v10_file_path.rename(problem_path)

        if v10_res.ok:
            try:
                v10_profile = self.profile_builder.build_profile(v10_res.data)
                self.profile_registry.set_profile(v10_profile)
            except Exception:
                self._logging("Error Loading profile, reverting to default profile.")
                self.profile_registry.set_profile_to_default(INTRAVERSION.V10)
                if PathManager.path_exists(v10_file_path, False):
                    v10_file_path.rename(problem_path)

    def load_v11(self):
        path = PathManager.create_folder_in_app_data("profiles")
        v11_file_path = Path(path) / self.v11_file_name
        v11_res = self.json_file_service.load(v11_file_path)
        problem_path = v11_file_path.with_name("problem_v11_profile.json")

        if not v11_res.ok or v11_res.data is None:
            self.profile_registry.set_profile_to_default(INTRAVERSION.V11)
            if PathManager.path_exists(v11_file_path, False):
                v11_file_path.rename(problem_path)

        if v11_res.ok:
            try:
                v11_profile = self.profile_builder.build_profile(v11_res.data)
                self.profile_registry.set_profile(v11_profile)
            except Exception:
                self._logging("Error Loading profile, reverting to default profile.")
                self.profile_registry.set_profile_to_default(INTRAVERSION.V10)
                if PathManager.path_exists(v11_file_path, False):
                    v11_file_path.rename(problem_path)
