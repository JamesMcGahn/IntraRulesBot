from dataclasses import dataclass
from playwright.sync_api import Page, BrowserContext

from ..ports import BrowserPort


@dataclass
class PlaywrightSession:
    browser_adapter: BrowserPort
    page: Page
    context: BrowserContext
