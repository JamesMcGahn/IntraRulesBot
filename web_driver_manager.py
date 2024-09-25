from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class WebDriverManager:

    def __init__(self, options=None):
        self.driver = None
        self.options = options
        # chrome_options.add_argument("--headless=new")
        self.init_driver()

    def init_driver(self):
        chrome_options = Options()
        if self.options:
            chrome_options.add_argument(self.options)
        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )

    def get_driver(self):
        return self.driver

    def close(self):
        if self.driver:
            self.driver.quit()
