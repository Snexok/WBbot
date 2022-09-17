from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random

SPEED = 1

class Card():
    card_button = lambda self, articul: self.driver.find_element(By.XPATH, f'//div[@id="{articul}"]/div/a/div/button')
    basket_btn = lambda self: self.driver.find_element(By.XPATH, '//span[contains(text(), "Добавить в корзину")]/..')
    basket_btns = lambda self: self.driver.find_elements(By.XPATH, '//span[contains(text(), "Добавить в корзину")]/..')
    page_back = lambda self: self.driver.back()

    def __init__(self, driver) -> None:
        self.driver = driver

    def add_card(self, article, target=False):
        """
        В каталоге выбираем карточку и нажимаем на нее
        Внутри карточки товара залипаем на нее и с возможно добавляем товар

        article - артикул
        target - признак того, что это тот самый товар, который мы искали
        """
        # Находим картинку
        img = self.driver.find_element(By.XPATH, f'//div[@id="{article}"]/div/a/div/div/img')
        hover = ActionChains(self.driver)

        # Наводимся на картинку
        hover.move_to_element(img).perform()

        sleep(SPEED*random.uniform(2, 4)+2)
        try:
            self.card_button(article).click()
        except:
            if target:
                hover.move_to_element(img).perform()
                self.card_button(article).click()
        sleep(1)
        if target:
            sleep(SPEED*random.uniform(3, 7))
            if random.randint(1, 2) == 2:
                self.see_images()
            self.to_basket()
        else:
            sleep(SPEED*random.uniform(1, 5))
            if random.randint(1, 20) == 3:
                if random.randint(1, 3) == 2:
                    self.see_images()
                self.to_basket()
                sleep(SPEED*2.5)
        sleep(SPEED*random.uniform(3, 5))
        self.close_card_modal()

        del hover


    def see_images(self):
        hover = ActionChains(self.driver)

        for slide in self.driver.find_elements(By.CLASS_NAME, 'slide'):
            hover.move_to_element(slide).perform()
            sleep(SPEED*random.uniform(1, 5))
            if random.randint(1, 4) == 3:
                return

    def choose_size(self):
        # Выбираем минимальный размер
        try:
            self.driver.find_element(By.XPATH, "//label[@class='j-size']").click()
            logger.info("✔Click to_basket")
        except:
            pass

    def to_basket(self):
        self.choose_size()
        try:
            self.basket_btn().click()
            logger.info("✔Click to_basket")
        except:
            pass
        try:
            for basket_btn in self.basket_btns():
                try:
                    basket_btn.click()
                except:
                    pass
            logger.info("✔Click to_basket")
        except:
            pass

    def close_card_modal(self):
        try:
            self.driver.find_element(By.CLASS_NAME, 'popup__close').click()
        except:
            self.page_back()
            sleep(2.5)
            print('.page_back(self.driver)')