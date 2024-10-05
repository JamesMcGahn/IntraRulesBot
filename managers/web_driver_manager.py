from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from base import QWorkerBase


class WebDriverManager(QWorkerBase):

    def __init__(self, options=None):
        super().__init__()
        self.driver = None
        self.options = options
        # chrome_options.add_argument("--headless=new")

    def init_driver(self):
        self.log_thread()
        chrome_options = Options()
        if self.options:
            chrome_options.add_argument(self.options)
        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )

    def get_driver(self):
        return self.driver

    def close(self):
        self.logging("Shutting down webdriver", "INFO")
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logging(f"There was an error in WebDriverManager: {e}")
