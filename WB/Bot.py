import random
from datetime import datetime, date, timedelta

from selenium.webdriver.common.by import By
from time import sleep
import json

from selenium.webdriver.support.wait import WebDriverWait

from TG.Admin import Admin
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Orders import Order, Orders
from WB.Pages.Basket import Basket
from WB.Browser import Browser
from WB.Pages.Catalog import Catalog
from WB.Utils import Utils

ARTICLE_LEN = 8

NOT_FOUND, READY, NOT_READY = range(3)

class Bot:
    def __init__(self, name="", data=None, driver=False):
        self.browser = Browser(driver)
        self.driver = self.browser.driver
        self.catalog = Catalog(self.browser)
        self.basket = Basket(self.browser)
        self.page = 'main'
        if data:
            self.data = data
        elif name:
            self.data = Bots_model.load(name)

    def open_bot(self):
        self.driver.maximize_window()
        self.browser.open_site('https://www.wildberries.ru')
        self.browser.load('./bots_sessions/' + self.data.name)
        self.browser.open_site('https://www.wildberries.ru')
        while self.browser.driver.current_url:
            sleep(60)


    def buy(self, data, post_place, order_id):
        self.driver.maximize_window()
        self.browser.open_site('https://www.wildberries.ru')
        self.browser.load('./bots_sessions/' + self.data.name)
        self.browser.open_site('https://www.wildberries.ru')

        report = {}
        for d in data:
            article_num, search_name, quantity, additional_data = d

            self.page = Utils.search(self.driver, search_name)  # catalog
            sleep(2)
            price = additional_data['price']
            self.catalog.price_filter(int(price * 0.75), int(price * 1.25))
            sleep(2)

            self.catalog.card_search(article_num)
            sleep(1)
        self.page = Utils.go_to_basket(self.driver)  # basket
        self.driver.refresh()
        sleep(2)

        articles = [str(d[0]) for d in data]
        report['articles'] = articles

        self.basket.delete_other_cards_in_basket(articles)

        report['prices'] = []
        for article in articles:
            price = self.basket.get_price(article)
            report['prices'] += [price]

        report['total_price'] = sum(report['prices'])

        report['quantities'] = []
        for article in articles:
            quantity = self.basket.get_quantity(article)
            report['quantities'] += [int(quantity)]

        sleep(3)
        self.basket.choose_post_place(post_place)
        # self.basket.choose_payment_method()
        shipment_date = self.basket.get_shipment_date()

        report['pred_end_date'] = self.get_end_date(shipment_date)
        report['qr_code'] = self.basket.get_qr_code(order_id, self.data.name)

        return report

    def get_data_cart(self, article, SAVE=False):
        self.driver.get("https://www.wildberries.ru/")
        sleep(2)
        self.driver.get("https://www.wildberries.ru/catalog/" + str(article) + "/detail.aspx?targetUrl=MI")
        data = {}

        names = WebDriverWait(self.driver, 60).until(lambda d: d.find_elements(By.XPATH, '//h1[@class="same-part-kt__header"]/span'))
        brand = names[0].text
        name = names[1].text

        data['name'] = {'brand': brand, 'name': name}

        stars = self.driver.find_element(By.XPATH, '//span[contains(@class, "stars-line")]').text

        data['stars'] = stars

        price = self.driver.find_element(By.XPATH, '//p[contains(@class, "price-block__price-wrap")]/span').text
        price = price[:price.index('₽')].replace(" ", "")

        data['price'] = int(price)

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

    async def check_readiness(self, articles, message):
        self.open_delivery()
        orders = self.get_all_orders()
        try:
            i = [all([order_article in articles for order_article in order.articles]) for order in orders].index(True)
        except:
            order = Orders.load()
            await message.answer(order.id + 'Артикулы не найдены')
        order = orders[i]
        if all([status == "" for status in order.statuses]):
            await message.answer(pred_end_date + ' Ваш заказ готов')
        else:
            pred_end_date = str(date.today() + timedelta(days=1))
            await Admin.wait_order_ended(self, pred_end_date, articles, message)

    @staticmethod
    def get_end_date(wb_day_month):
        """
        wb_day_month - День и месяц с в формате Wildberries
        """
        month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

        month = 0
        for i, m in enumerate(month_list):
            if m in wb_day_month:
                index = wb_day_month.index(m)
                wb_day_month = wb_day_month[:index - 1]
                month = i + 1
                break

        day = int(wb_day_month.split('-')[0])

        year = datetime.today().year

        return str(date(year, month, day))

    def get_all_orders(self) -> list:
        orders = []
        for order_row in self.driver.find_elements(By.XPATH, ''):
            order = Order()
            order.pup_address = order_row.find_element(By.XPATH, '')
            item_imgs = order_row.find_elements(By.XPATH, '')
            img_ext_len = len('-1.avif')
            order.articles = [img_href[-img_ext_len-ARTICLE_LEN:-img_ext_len] for img_href in item_imgs]
            order.statuses = order_row.find_elements(By.XPATH, '')

            orders += [order]
        return orders