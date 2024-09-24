import json
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from actions_worker import ActionsWorker
from conditions_worker import ConditionsWorker
from keys import keys
from login_manager import LoginManager
from rule_worker import RuleWorker
from services.logger import Logger
from trigger_worker import TriggerWorker
from web_element_interactions import WaitConditions, WebElementInteractions


class WebScrape:
    def __init__(self, url):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )
        self.wELI = WebElementInteractions(self.driver)
        self.not_available = []
        self.source = None
        self.url = url

        with open("avaya_rules.json") as f:
            self.config_data = json.load(f)

    def close(self):
        self.driver.close()

    def init_driver(self):
        pass

    def run_webdriver(
        self,
    ):
        try:
            self.driver.get(self.url)
            Logger()
            # ---- LOGIN
            # TODO: put in fn
            login = LoginManager(self.driver, keys["login"], keys["password"])
            login.login()

            # --- Wait for Page Load -> Move to Rules Page
            if self.wELI.wait_for_element(
                10, By.ID, "ctl00_radTabStripSubNavigation", WaitConditions.PRESENCE
            ):
                self.driver.get(self.url + "/ManagerConsole/Delivery/Rules.aspx")

                sleep(3)
                for rule in self.config_data["rules"]:
                    ruleworker = RuleWorker(self.driver, rule)
                    ruleworker.do_work()
                sleep(30)

        except Exception as e:
            print(e)
        finally:
            self.close()


run = WebScrape(keys["url"])
run.run_webdriver()


# except Exception as e:
#                         print(e)
#                     except NoSuchFrameException:
#                         print(
#                             "Iframe not found, make sure you're identifying the iframe correctly."
#                         )
