from dataclasses import dataclass, field, fields

from .map_log_settings import LogSettings
from .map_login_settings import LoginSettings


@dataclass
class AppSettings:
    login: LoginSettings = field(default_factory=LoginSettings)
    log: LogSettings = field(default_factory=LogSettings)

    def get_fields_list(self):
        return [f for f in fields(self)]
