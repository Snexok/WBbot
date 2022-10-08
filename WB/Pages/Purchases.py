from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class Purchases:
    def __init__(self, browser):
        self.driver = browser.driver

    def get_all_articles(self):
        cards_elements = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_elements(By.XPATH, f'//div[contains(@class, "archive-item__img-wrap")]'))
        articles = [c_e.get_attribute("data-popup-nm-id") for c_e in cards_elements]
        return articles

    def check_article(self, article):
        articles = self.get_all_articles()
        if not articles:
            logger.info("Purchases are empty")
            return False
        else:
            return article in articles