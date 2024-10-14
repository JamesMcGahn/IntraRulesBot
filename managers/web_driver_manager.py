from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from base import QWorkerBase


class WebDriverManager(QWorkerBase):
    """
    Manages the WebDriver instance for Selenium-based automation, handling initialization and shutdown.

    Attributes:
        driver (webdriver.Chrome): The Selenium Chrome WebDriver instance.
        options (str or None): Optional arguments to pass to the Chrome WebDriver on initialization.

    Args:
        options (str, optional): Options to pass to the Chrome WebDriver. Defaults to None.
    """

    def __init__(self, options: Optional[str] = None):

        super().__init__()
        self.driver = None
        self.options = options
        # chrome_options.add_argument("--headless=new")

    def init_driver(self) -> None:
        """
        Initialize the Chrome WebDriver with the specified options.
        Logs the thread information and sets up the WebDriver instance.
        """
        self.log_thread()
        chrome_options = Options()
        if self.options:
            chrome_options.add_argument(self.options)
        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )

    def get_driver(self) -> Optional[webdriver.Chrome]:
        """
        Return the initialized Chrome WebDriver instance.

        Returns:
            Optional[webdriver.Chrome]: The Chrome WebDriver instance, or None if not initialized.
        """
        return self.driver

    def close(self) -> None:
        """
        Close and shut down the Chrome WebDriver. Logs the shutdown process and handles any errors during shutdown.
        """
        self.logging("Shutting down webdriver", "INFO")
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logging(f"There was an error in WebDriverManager: {e}")
