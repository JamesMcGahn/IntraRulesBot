from dataclasses import dataclass, field, fields

from .map_log_settings import LogSettings
from .map_login_settings import LoginSettings
from .map_browser_settings import BrowserSettings


@dataclass
class AppSettings:
    login: LoginSettings = field(default_factory=LoginSettings)
    log: LogSettings = field(default_factory=LogSettings)
    browser: BrowserSettings = field(default_factory=BrowserSettings)

    def get_fields_list(self):
        return [f for f in fields(self)]
