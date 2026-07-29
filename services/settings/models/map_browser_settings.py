from dataclasses import dataclass
from typing import ClassVar

from ..enums import SETTINGSCATEGORIES, SETTINGSWIDGETTYPE


from ..validators.browser_validators import (
    validate_browser_headless,
    validate_browser_move_delay_speed,
)
from .base_category_map import SettingsCategoryBase
from .settings_field_helper import setting


@dataclass
class BrowserSettings(SettingsCategoryBase):
    schema_name: ClassVar[str] = SETTINGSCATEGORIES.BROWSER
    display_name: ClassVar[str] = "Browser Settings"
    browser_headless: str = setting(
        key="browser_headless",
        default="False",
        category=SETTINGSCATEGORIES.BROWSER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Hide Browser:",
        verify_btn_text="Save",
        secure=False,
        combo_box=["True", "False"],
        verify=validate_browser_headless,
    )
    browser_move_delay_speed: int = setting(
        key="browser_move_delay_speed",
        default=500,
        category=SETTINGSCATEGORIES.BROWSER,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Movement Delay:",
        verify_btn_text="Save",
        secure=False,
        folder_icon=False,
        verify=validate_browser_move_delay_speed,
    )
