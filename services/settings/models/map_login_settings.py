from dataclasses import dataclass
from typing import ClassVar

from ..enums import SETTINGSCATEGORIES, SETTINGSWIDGETTYPE

# TODO add validators
from ..validators.login_validators import (
    validate_password,
    validate_platform_version,
    validate_tenant,
    validate_user_name,
)
from .base_category_map import SettingsCategoryBase
from .settings_field_helper import setting
from base.enums import INTRAVERSION


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
        verify=validate_user_name,
        tied_fields=[
            ("password", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("tenant", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("platform_version", SETTINGSWIDGETTYPE.COMBO_BOX),
        ],
        async_verify_group="validate_intra_login",
    )
    password: str = setting(
        key="login_password",
        default="",
        category=SETTINGSCATEGORIES.LOGIN,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Password:",
        verify_btn_text="Verify Password",
        secure=True,
        folder_icon=False,
        verify=validate_password,
        hide_secure_text=True,
        tied_fields=[
            ("user_name", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("tenant", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("platform_version", SETTINGSWIDGETTYPE.COMBO_BOX),
        ],
        async_verify_group="validate_intra_login",
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
        verify=validate_tenant,
        tied_fields=[
            ("user_name", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("password", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("platform_version", SETTINGSWIDGETTYPE.COMBO_BOX),
        ],
        async_verify_group="validate_intra_login",
    )
    platform_version: str = setting(
        key="login_platform_version",
        default="V10",
        category=SETTINGSCATEGORIES.LOGIN,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Tenant Version:",
        verify_btn_text="Save Tenant Version",
        secure=False,
        combo_box=[INTRAVERSION.V10.value, INTRAVERSION.V11.value],
        verify=validate_platform_version,
        tied_fields=[
            ("user_name", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("password", SETTINGSWIDGETTYPE.LINE_EDIT),
            ("tenant", SETTINGSWIDGETTYPE.LINE_EDIT),
        ],
        async_verify_group="validate_intra_login",
    )
