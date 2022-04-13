from selenium.webdriver.common.by import By
from time import sleep
import json

from Basket import Basket
from Browser import Browser
from Catalog import Catalog
from Utils import Utils


class Bot:
    def __init__(self, driver=False):
        self.browser = Browser(driver)
        self.driver = self.browser.driver
        self.utils = Utils(self.browser)
        self.catalog = Catalog(self.browser)
        self.basket = Basket(self.browser)
        self.page = 'main'

    def buy(self, data):
        order_name = ""
        report = {}
        for d in data:
            article_num, search_name, quantity = d
            order_name += article_num

            self.page = self.utils.search(search_name)  # catalog
            sleep(2)

            self.catalog.card_search(article_num)
        self.page = self.utils.go_to_basket()  # basket
        sleep(1)
        articles = [str(d[0]) for d in data]
        self.basket.delete_other_cards_in_basket(articles)
        sleep(3)
        post_place = "123"
        self.basket.choose_post_place(post_place)
        self.basket.choose_payment_method()
        report['qr_code'] = self.basket.get_qr_code('order_' + order_name + '.png')

    def get_data_cart(self, article, SAVE=False):
        self.driver.get("https://www.wildberries.ru/")
        sleep(2)
        self.driver.get("https://www.wildberries.ru/catalog/" + article + "/detail.aspx?targetUrl=MI")

        data = {}

        names = self.driver.find_elements(By.XPATH, '//h1[@class="same-part-kt__header"]/span')
        brand = names[0].text
        name = names[1].text

        data['name'] = {'brand': brand, 'name': name}

        stars = self.driver.find_element(By.XPATH, '//span[contains(@class, "stars-line")]').text

        data['stars'] = stars

        price = self.driver.find_element(By.XPATH, '//p[contains(@class, "price-block__price-wrap")]/span').text
        price = price[:price.index('₽')].replace(" ", "")

        data['price'] = price

        try:
            self.driver.find_element(By.XPATH,
                                     '//button[contains(@class, "collapsible__toggle") and text()="Развернуть описание"]').click()
        except:
            pass
        try:
            self.driver.find_element(By.XPATH,
                                     '//button[contains(@class, "collapsible__toggle") and text()="Развернуть характеристики"]').click()
        except:
            pass
        try:
            descriptions = self.driver.find_elements(By.XPATH,
                                                     '//h2[contains(@class, "section-header") and text()="Описание"]/../../div')

            description = descriptions[1].text
            data['description'] = description

            tables = descriptions[2].find_elements(By.XPATH, './/div/table')
            characters = []
            for table in tables:
                _characters = []
                character_main = table.find_element(By.XPATH, './/caption').text
                _characters.append({"name": character_main, "characters": []})
                char_names = table.find_elements(By.XPATH, './/tbody/tr/th/span')
                char_values = table.find_elements(By.XPATH, './/tbody/tr/td')
                for i in range(len(char_names)):
                    _characters[-1]["characters"].append({'name': char_names[i].text, 'value': char_values[i].text})
                characters += _characters
            data['characters'] = characters
        except:
            pass
        try:
            composition = self.driver.find_element(By.XPATH,
                                                   '//h2[contains(@class, "section-header") and text()="Состав"]/../div/div').text
            if composition:
                data['composition'] = composition
        except:
            pass

        if SAVE:
            with open('card_data/' + article + '.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        else:
            return data
