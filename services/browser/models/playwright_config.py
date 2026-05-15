from dataclasses import dataclass


@dataclass
class PlaywrightConfig:
    headless: bool = False
    slow_mo: int = 500
    load_cookies: bool = False
