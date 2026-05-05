from dataclasses import dataclass
from typing import ClassVar

from ..enums import SETTINGSCATEGORIES, SETTINGSWIDGETTYPE

# TODO add validators
from ..validators.log_validators import (
    validate_log_file_max_mbs,
    validate_log_level,
)
from .base_category_map import SettingsCategoryBase
from .settings_field_helper import setting


@dataclass
class LoginSettings(SettingsCategoryBase):
    schema_name: ClassVar[str] = SETTINGSCATEGORIES.LOGIN
    display_name: ClassVar[str] = "Login Settings"
    user_name: str = setting(
        key="login_user_name",
        default="",
        category=SETTINGSCATEGORIES.LOGIN,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="User name:",
        verify_btn_text="Verify Username",
        secure=False,
        folder_icon=False,
        verify=validate_log_file_max_mbs,
    )
    password: str = setting(
        key="login_password",
        default="",
        category=SETTINGSCATEGORIES.LOGIN,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Password:",
        verify_btn_text="Verify Password",
        secure=False,
        folder_icon=False,
        verify=validate_log_file_max_mbs,
        hide_secure_text=True,
    )
    tenant: str = setting(
        key="login_tenant",
        default="",
        category=SETTINGSCATEGORIES.LOGIN,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Tenant:",
        verify_btn_text="Save Tenant",
        secure=False,
        folder_icon=False,
        verify=validate_log_file_max_mbs,
    )
    platform_version: str = setting(
        key="login_platform_version",
        default="V10",
        category=SETTINGSCATEGORIES.LOGIN,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Tenant Version:",
        verify_btn_text="Save Tenant Version",
        secure=False,
        combo_box=["V10", "V11"],
        verify=validate_log_level,
    )
