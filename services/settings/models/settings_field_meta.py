from dataclasses import dataclass
from typing import Callable, Optional

from ..enums import SETTINGSCATEGORIES, SETTINGSWIDGETTYPE


@dataclass
class SettingsFieldMeta:
    key: str
    label_text: str
    category: SETTINGSCATEGORIES
    widget_type: SETTINGSWIDGETTYPE
    verify_btn_text: str
    secure: bool = False
    folder_icon: bool = False
    combo_box: list[str] | None = None
    verify: Optional[Callable] = None
    hide_secure_text: bool = False
    tied_fields: list[str] | None = None
    async_verify_group: str | None = None
