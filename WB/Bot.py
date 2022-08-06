from datetime import datetime, date, timedelta

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from time import sleep
import json

from selenium.webdriver.support.wait import WebDriverWait

from aiogram import Bot as TG_Bot

from TG.Models.Bots import Bots as Bots_model
from TG.Models.Admins import Admins as Admins_model
from TG.Models.Orders import Order, Orders
from WB.Pages.Basket import Basket
from WB.Browser import Browser
from WB.Pages.Catalog import Catalog
from WB.Utils import Utils
from configs import config

API_TOKEN = config['tokens']['telegram']

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
            self.data = Bots_model.load(name=name)

    def open_bot(self, manual=True):
        self.driver.maximize_window()
        if self.data.type == "WB":
            path = 'https://www.wildberries.ru'
        elif self.data.type == "WB_Partner":
            path = 'https://seller.wildberries.ru/'
        self.browser.open_site(path)
        self.browser.load(f'./bots_sessions/{self.data.name}')
        self.browser.open_site(path)
        if manual:
            try:
                while self.browser.driver.current_url:
                    sleep(60)
            except:
                pass

    def search(self, data):
        report = {}
        report['bot_name'] = self.data.name
        report['bot_username'] = self.data.username
        print(f'Bot {self.data.name} started')
        for d in data:
            if d['search_key']:
                Utils.search(self.driver, d['search_key'])
            elif d['category']:
                Utils.open_category(self.driver, d['category'])
            else:
                print("Не указан не ключ поиска, не категория")

            sleep(2)
            price = d['additional_data']['price']
            self.catalog.price_filter(int(price * 0.75), int(price * 1.25))
            sleep(2)

            self.catalog.card_search(d['article'])
            sleep(1)
        sleep(2)

        report['inn'] = data[0]['inn']


        articles = [str(d['article']) for d in data]
        report['articles'] = articles
        print(self.data.name, articles)

        return report

    def check_basket(self, article):
        basket_cnt = Utils.get_basket_cnt(self.driver)
        if basket_cnt:
            if int(basket_cnt)>0:
                Utils.go_to_basket(self.driver)
                return self.basket.check_card(article)

        return False

    def buy(self, report, post_place, order_id):
        sleep(1)
        try:
            self.page = Utils.go_to_basket(self.driver)  # basket
        except:
            sleep(3)
            self.page = Utils.go_to_basket(self.driver)  # basket

        self.driver.refresh()
        sleep(2)

        self.basket.delete_other_cards_in_basket(report['articles'])

        report['prices'] = []
        for article in report['articles']:
            price = self.basket.get_price(article)
            report['prices'] += [price]

        report['total_price'] = sum(report['prices'])

        report['quantities'] = []
        for article in report['articles']:
            quantity = self.basket.get_quantity(article)
            report['quantities'] += [int(quantity)]

        sleep(3)
        print("in WB\Bot", post_place)
        self.basket.choose_post_place(post_place)
        self.basket.choose_payment_method()
        shipment_date = self.basket.get_shipment_date()

        report['pred_end_date'] = datetime.fromisoformat(self.get_end_date(shipment_date))
        report['qr_code'] = self.basket.get_qr_code(order_id, self.data.name)

        return report

    def re_buy(self, report, post_place, order_id):
        self.page = Utils.go_to_basket(self.driver)  # basket
        self.driver.refresh()
        sleep(2)

        self.basket.delete_other_cards_in_basket(report['articles'])

        report['prices'] = []
        for article in report['articles']:
            price = self.basket.get_price(article)
            report['prices'] += [price]

        report['total_price'] = sum(report['prices'])

        report['quantities'] = []
        for article in report['articles']:
            quantity = self.basket.get_quantity(article)
            report['quantities'] += [int(quantity)]

        sleep(3)
        print("in WB\Bot", post_place)
        self.basket.choose_post_place(post_place)
        self.basket.choose_payment_method("Оплата балансом")
        shipment_date = self.basket.get_shipment_date()

        report['pred_end_date'] = datetime.fromisoformat(self.get_end_date(shipment_date))
        self.basket.pay()
        report["payment_datetime"] = str(datetime.now())
        report["payment"] = True

        return report

    def get_data_cart(self, article, SAVE=False):
        self.driver.get("https://www.wildberries.ru/")
        sleep(2)
        self.driver.get(f"https://www.wildberries.ru/catalog/{str(article)}/detail.aspx?targetUrl=MI")
        data = {}

        try:
            names = WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements(By.XPATH, '//h1[@class="same-part-kt__header"]/span'))
            brand = names[0].text
            name = names[1].text
        except:
            names = WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.XPATH, '//div[@class="product-page__header"]'))
            brand = names.find_element(By.XPATH, './span').text
            name = names.find_element(By.XPATH, './h1').text
            print(brand,name)

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
            with open('card_data/{article}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        else:
            return data

    async def check_readiness(self, orders, message, wait_order_ended):
        bot = TG_Bot(token=API_TOKEN)
        sleep(1)
        # открываем страницу с заказами бота
        self.open_delivery()
        sleep(2)
        # полуыаем все заказы бота
        local_orders = self.get_all_orders()
        for _order in local_orders:
            print("local_orders", _order)
        sleep(1)

        for order in orders:
            print("local_orders[0].pup_address", local_orders[0].pup_address)
            print("order.pup_address", order.pup_address)
            # фильтруем заказы бота адресу
            local_orders_by_address = [_order for _order in local_orders if _order.pup_address == order.pup_address]
            print(local_orders_by_address)
            # берем единственное совпадение по адресу
            _order = local_orders_by_address[0]

            statuses = []
            for article in order.articles:
                for i in range(len(_order.articles)):
                    _article = _order.articles[i]
                    print("article: ", article)
                    print("_article: ", _article)
                    if article == _article:
                        for _status in _order.statuses:
                            print("_status: ", _status)
                            if _status != "Платный отказ":
                                statuses += [_status]
            print(statuses)

            if len(statuses) < len(order.articles):
                await message.answer(f'Один из артикулов заказа {order.id} не был найден.\n '
                                     f'Артикулы {str(order.articles)}')
            else:
                order.set(statuses=statuses)
                order.set(code_for_approve=_order.code_for_approve)
                for i, status in enumerate(statuses):
                    if status in ["Готов к получению", "Отгружено по данным Продавца", 'Готов к выдаче', 'Прибыл на пункт выдачи']:
                        msg_pup = 'Заказ готов\n' + \
                                  f'Код: {order.code_for_approve}\n' + \
                                  f'Фио: {order.bot_surname}\n' + \
                                  f'Адрес: {order.pup_address}\n' + \
                                  f'Артикул: {order.articles[i]}'
                        msg_admin = msg_pup + '\n' + \
                                    f'Номер заказа: {order.number}\n' + \
                                    f'Id заказа: {order.id}\n'

                        order.set(end_date=date.today())
                        order.set(active=False)

                        admin = Admins_model().get_sentry_admin()
                        print(admin.id)
                        await bot.send_message(admin.id, msg_admin, parse_mode="HTML")
                        if order.pup_tg_id:
                            await bot.send_message(order.pup_tg_id, msg_pup, parse_mode="HTML")
                    else:
                        pred_end_date = ''
                        for status in order.statuses:
                            if 'Ожидается' in status:
                                msg = status
                                admin = Admins_model().get_sentry_admin()
                                pred_end_date = datetime.fromisoformat(self.get_end_date(status[len('Ожидается '):]))
                                await bot.send_message(admin.id, msg, parse_mode="HTML")
                        if not pred_end_date:
                            pred_end_date = datetime.fromisoformat(str(date.today() + timedelta(days=1)))
                    print('order ', order)
                    order.update()

    @staticmethod
    def get_end_date(wb_day_month) -> str:
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
        print(wb_day_month)
        day = int(wb_day_month.split('-')[0])

        year = date.today().year

        return str(date(year, month, day))

    def get_all_orders(self) -> list:
        orders = []
        sleep(2)
        for order_row in self.driver.find_elements(By.XPATH, '//div[@class="delivery-block__content"]'):
            order = Order()
            order.pup_address = order_row.find_element(By.XPATH,
                                                       './div/div/div[contains(@class, "delivery-address__info")]').text
            item_imgs = order_row.find_elements(By.XPATH, './div/ul/li/div/div/img')
            img_ext_len = len('/images/c516x688/1.jpg')
            order.articles = [img.get_attribute('src')[-img_ext_len - ARTICLE_LEN:-img_ext_len] for img in item_imgs]
            statuses = order_row.find_elements(By.XPATH,
                                               './div/ul/li/div/div/div[@class="goods-list-delivery__price-status"]')
            order.statuses = [status.text for status in statuses]  # Ожидается 19-21 мая, Отсортирован в сортировочном центре, В пути на пункт выдачи, Готов к выдаче
            try:
                order.code_for_approve = order_row.find_element(By.XPATH,
                                                                "./div/div/div[contains(@class,'delivery-code__value')]").text
            except:
                order.code_for_approve = ""

            orders += [order]
        return orders

    def open_delivery(self):
        sleep(3)
        hover = ActionChains(self.driver)

        profile_btn = self.driver.find_element(By.XPATH, "//span[contains(@class,'navbar-pc__icon--profile')]")
        hover.move_to_element(profile_btn).perform()
        sleep(3)
        delivery_btn = self.driver.find_element(By.XPATH,
                                                "//span[text()='Доставки']/../../a[contains(@class,'profile-menu__link')]")
        delivery_btn.click()

    def expect_payment(self):
        payment = False
        print("expect_payment run")
        i = 0
        while True:
            try:
                payment = True if self.driver.find_element(By.XPATH,
                                                           '//h1[text()="                Ваш заказ подтвержден                "]') else False
                break
            except:
                if i < 360:
                    sleep(1)
                else:
                    break
                i += 1
        start_datetime = str(datetime.now())
        return {'payment': payment, 'datetime': start_datetime}
