import asyncio
import sys

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from time import sleep
import random

from selenium.webdriver.support.wait import WebDriverWait

from TG.Models.Delivery import Delivery_Model

ARTICLE_LEN = 10

class Delivery():
    def __init__(self, browser) -> None:
        self.driver = browser.driver
        self.local_delivery = None

    def get_deliveries_by_address(self, target_address) -> Delivery_Model:
        delivery = Delivery_Model()
        sleep(5)
        for delivery_row in self.driver.find_elements(By.XPATH, '//div[@class="delivery-block__content"]'):
            address = delivery_row.find_element(By.XPATH,
                                                       './div/div/div[contains(@class, "delivery-address__info")]').text
            if address == target_address:
                delivery.pup_address = address
                item_imgs = delivery_row.find_elements(By.XPATH, './div/ul/li/div/div/img')
                img_ext_len = len('/images/c516x688/1.jpg') # Раньше было так
                # img_ext_len = len('-1.jpg')
                # пример, если артикул 9 символов "/117567980" ⬇
                logger.info([img.get_attribute('src') for img in item_imgs])
                delivery.articles = [''.join(img.get_attribute('src')[-img_ext_len - ARTICLE_LEN:-img_ext_len].split('/')[-1]) for img in item_imgs]
                statuses = delivery_row.find_elements(By.XPATH,
                                                   './div/ul/li/div/div/div[@class="goods-list-delivery__price-status"]')
                delivery.statuses = [status.text for status in statuses if status.text != "Платный отказ"]  # Ожидается 19-21 мая, Отсортирован в сортировочном центре, В пути на пункт выдачи, Готов к выдаче
                try:
                    delivery.code_for_approve = delivery_row.find_element(By.XPATH,
                                                                    "./div/div/div[contains(@class,'delivery-code__value')]").text
                except:
                    delivery.code_for_approve = ""

        self.local_delivery = delivery

        return delivery

    def update_statuses(self, delivery):
        delivery.statuses = []
        for article in set(delivery.articles):
            for i, _article in enumerate(self.local_delivery.articles):

                logger.info(f"article: {article}\n"
                            f"_article: {_article}")

                # Обновляем статус заказа
                if _article == article:
                    _status = self.local_delivery.statuses[i]
                    delivery.statuses += [_status]

                    logger.info(f"_status: {_status}")

        logger.info(delivery.statuses)
