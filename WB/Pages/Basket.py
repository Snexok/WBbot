from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random

from selenium.webdriver.support.wait import WebDriverWait

from WB.Card import Card


class Basket():
    def __init__(self, browser) -> None:
        self.driver = browser.driver
        self.card = Card(self.driver)

    def check_card(self, article):
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements(By.XPATH, f'//a[contains(@href, "{article}") and contains(@class,"good-info__title")]'))
            return True
        except:
            return False

    # Рефакторинг под множество артикулов
    def delete_other_cards_in_basket(self, articles):
        logger.info("start")
        hover = ActionChains(self.driver)
        while True:
            try:
                card_names = self.driver.find_elements(By.XPATH, '//a[contains(@href, "catalog") and @class="good-info__title j-product-popup"]')
            except:
                logger.info("basket is empty")
                user_notify_msg = "❌ Ошибка выкупа ❌\n" \
                                  "😓 Прости, корзина этого бота пуста 😓\n\n" \
                                  "Скоро будет фича, позволяющая запустить поиск в такой ситуации"
                return user_notify_msg

            card = card_names[random.choice(list(range(len(card_names))))]

            card_name_href = card.get_attribute('href')
            catalog_url_len = len('https://www.wildberries.ru/catalog/')

            #
            if not any(a in card_name_href for a in articles):
                counter = card.find_element(By.XPATH, '../../../div[contains(@class,"count")]')
                hover.move_to_element(counter).perform()
                sleep(random.uniform(1, 5))
                counter.find_element(By.CLASS_NAME, 'btn__del').click()

            # Если убрали все лишние товары
            if len(card_names) <= len(articles):
                card_names = [card.get_attribute('href')[catalog_url_len:catalog_url_len + 8]
                              for card in card_names]
                # Могут встречаться артикулы с длинной 7, а не 8. Их вырезаем не корректно
                card_articles = [card_name.replace('/', '') for card_name in card_names]
                card_articles.sort()
                articles.sort()
                # Проверка, что все карточки из списка искаемых артикулов
                are_all_cards_targeted = all([any([card_article in articles[i] for i in range(len(articles))]) for card_article in card_articles])
                if not are_all_cards_targeted:
                    for card_article in card_articles:
                        # Удаление карточки, которая не является целевой
                        if card_article not in articles:
                            manual_msg = "Мы потеряли минимум один товар и минимум один товар в корзине пустой, требуется ручноре действие"
                            logger.info(manual_msg)
                            return manual_msg
                            # counter = card.find_element(By.XPATH, '../../../div[contains(@class,"count")]')
                            # hover.move_to_element(counter).perform()
                            # sleep(random.uniform(1, 5))
                            # counter.find_element(By.CLASS_NAME, 'btn__del').click()
                else:
                    logger.info("end")
                    return False

    def choose_post_place(self, address, rerun=False):
        logger.info(address)
        if not rerun:
            try:
                self.driver.find_element(By.XPATH,
                                         '//h2[text()="Способ доставки"]/../../div[text()="Выбрать адрес доставки"]').click()
                logger.info("choose post place")
            except:
                self.driver.find_element(By.XPATH,
                                         '//h2[text()="Способ доставки"]/../button/span[text()="Изменить"]').click()
                logger.info("edit post place")
            sleep(1)

            try:
                self.driver.find_element(By.XPATH,
                                    f'//ul[contains(@class,"history__list")]/li/label/span/span[contains(@class,"history__address") and contains(text(),"{address}")]').click()
                sleep(1)
                self.driver.find_element(By.XPATH, '//button[@class="popup__btn-main"]').click()
                logger.info("history__address finish")
                sleep(2)
                return
            except:
                try:
                    self.driver.find_element(By.XPATH, '//button[text()="Выбрать адрес доставки"]').click()
                    logger.info("choose post place")
                except:
                    self.driver.find_element(By.XPATH, '//button[text()="Выбрать другой адрес"]').click()
                    logger.info("choose other post place")

        sleep(2)
        address_input = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]'))
        address_input.send_keys(Keys.CONTROL + "a")
        address_input.send_keys(Keys.DELETE)
        address_input.send_keys(address)
        address_input.send_keys(Keys.ENTER)
        logger.info("Y.maps entered post place")

        sleep(2)
        self.driver.find_element(By.XPATH, '//ymaps[text()="Найти"]').click()

        sleep(2)
        try:
            self.driver.find_element(By.XPATH, '//ymaps[contains(@class, "__first")]').click()
            logger.info("Y.maps choose first post place in drop down")
        except:
            logger.info("Y.maps dont entered post place")
            pass

        sleep(2)
        self.driver.find_element(By.XPATH, f'//span[contains(text(), "{address}")]').click()

        sleep(2)
        try:
            self.driver.find_element(By.XPATH, '//div[@class="balloon-content-block"]/button').click()
            logger.info("Y.maps click choose btn")
        except:
            sleep(2)
            self.choose_post_place(address, rerun=True)
            logger.info("re choose post place")
            return

        sleep(2)
        self.driver.find_element(By.XPATH, '//button[@class="popup__btn-main"]').click()
        logger.info("finish")

        sleep(2)

    def choose_payment_method(self, payment_method="Оплата по QR-коду"):
        logger.info(payment_method)
        try:
            self.driver.find_element(By.XPATH,
                                     '//h2[text()="Способ оплаты"]/../../div[text()="Выбрать способ оплаты"]').click()
            sleep(1)
            self.driver.find_element(By.XPATH, f'//span[contains(text(),"{payment_method}")]').click()
            sleep(2)
            self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
            sleep(2)
        except:
            if self.driver.find_element(By.XPATH, '//span[@class="pay__text"]').text == payment_method:
                return
            self.driver.find_element(By.XPATH, '//h2[text()="Способ оплаты"]/../button/span[text()="Изменить"]').click()
            sleep(1)
            self.driver.find_element(By.XPATH, f'//span[contains(text(),"{payment_method}")]').click()
            sleep(2)
            self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
            sleep(2)

    def get_qr_code(self, order_id, bot_name):
        file_name = 'order_' + str(order_id) + '_' + bot_name + '.png'
        self.driver.find_element(By.XPATH, '//button[text()="                Оплатить заказ                "]').click()
        sleep(2)
        # self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
        # sleep(2)
        svg = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element(By.XPATH, '//div[@class="qr-code__value"]'))
        self.save_qr_code(svg, file_name)

        return file_name

    def pay(self):
        self.driver.find_element(By.XPATH, '//button[text()="                Оплатить заказ                "]').click()

    def save_qr_code(self, svg, file_name):
        svg.screenshot(file_name)

    def get_price(self, article):
        list_item_price = self.driver.find_elements(
                            By.XPATH, f'//a[contains(@href, "{article}") and contains(@href, "catalog") '
                                      'and @class="good-info__title j-product-popup"]/../../../'
                                      'div[@class="list-item__price"]/div')
        price = int(list_item_price[0].text[:-2].replace(" ", ""))
        return price

    def get_quantity(self, article):
        count_input_number = self.driver.find_element(By.XPATH, f'//a[contains(@href, "{article}") and contains(@href, '
                                                         '"catalog") and @class="good-info__title '
                                                         'j-product-popup"]/../../../div[contains(@class,'
                                                         '"count")]/div[contains(@class,"count__wrap")]/div[contains('
                                                         '@class,"count__input-number")]/input')
        quantity = count_input_number.get_attribute('value')
        return quantity

    def get_shipment_date(self):
        return self.driver.find_element(By.XPATH, '//span[text()="Дата"]/../span[@class="b-link"]').text
