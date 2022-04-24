from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random

from WB.Card import Card
from WB.Utils import Utils


class Basket():
    def __init__(self, browser) -> None:
        self.driver = browser.driver
        self.card = Card(self.driver)

    def check_card(self, card):
        card.click()


    # Рефакторинг под множество артикулов
    def delete_other_cards_in_basket(self, articles):
        hover = ActionChains(self.driver)
        while True:
            card_names = self.driver.find_elements(By.XPATH, '//a[contains(@href, "catalog") and @class="good-info__title j-product-popup"]')
            card = card_names[random.choice(list(range(len(card_names))))]
            if random.randint(0, 5) == 3:
                self.check_card(card)
            card_name_href = card.get_attribute('href')
            card_name = card_name_href[len('https://www.wildberries.ru/catalog/'):len('https://www.wildberries.ru/catalog/')+8]
            if not any(a in card_name_href for a in articles):
                counter = card.find_element(By.XPATH, '../../../div[contains(@class,"count")]')
                hover.move_to_element(counter).perform()
                sleep(random.uniform(1,5))
                counter.find_element(By.CLASS_NAME, 'btn__del').click()
            if len(card_names)<=len(articles):
                card_names = [card.get_attribute('href')[len('https://www.wildberries.ru/catalog/'):len('https://www.wildberries.ru/catalog/')+8] for card in card_names]
                card_names.sort()
                articles.sort()
                print(card_names)
                print(articles)
                if card_names != articles:
                    for card_name in card_names:
                        if card_name in articles:
                            counter = card_name.find_element(By.XPATH, '../../../div[contains(@class,"count")]')
                            hover.move_to_element(counter).perform()
                            sleep(random.uniform(1, 5))
                            counter.find_element(By.CLASS_NAME, 'btn__del').click()
                else:
                    return





    def choose_post_place(self, adress, req=False):
        if not req:
            self.driver.find_element(By.XPATH, '//h2[text()="Способ доставки"]/../../div[text()="Выбрать адрес доставки"]').click()
            sleep(1)
            self.driver.find_element(By.XPATH, '//button[text()="Выбрать адрес доставки"]').click()
        sleep(2)
        self.driver.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]').send_keys(Keys.CONTROL + "a")
        self.driver.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]').send_keys(Keys.DELETE)
        self.driver.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]').send_keys(adress)
        self.driver.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]').send_keys(Keys.ENTER)
        sleep(2)
        # self.driver.find_element(By.XPATH, '//ymaps[text()="Найти"]').click()
        sleep(2)
        try:
            self.driver.find_element(By.XPATH, '//ymaps[contains(@class, "__first")]').click()
        except:
            pass
        sleep(2)
        self.driver.find_element(By.XPATH, '//span[contains(text(), "'+ adress +'")]').click()
        sleep(2)
        try:
            self.driver.find_element(By.XPATH, '//div[@class="balloon-content-block"]/button').click()
        except:
            sleep(2)
            self.choose_post_place(adress, req=True)

        sleep(2)
        self.driver.find_element(By.XPATH, '//button[@class="popup__btn-main"]').click()
        sleep(2)
        
    def choose_payment_method(self, payment_method="Оплата по QR-коду"):
        try:
            self.driver.find_element(By.XPATH,
                                     '//h2[text()="Способ оплаты"]/../../div[text()="Выбрать способ оплаты"]').click()
            sleep(1)
            self.driver.find_element(By.XPATH, '//span[text()="' + payment_method + '"]').click()
            sleep(2)
            self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
            sleep(2)
        except:
            self.driver.find_element(By.XPATH, '//h2[text()="Способ оплаты"]/../button/span[text()="Изменить"]').click()
            sleep(1)
            self.driver.find_element(By.XPATH, '//span[text()="' + payment_method + '"]').click()
            sleep(2)
            self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
            sleep(2)
        
    def get_qr_code(self, order_id, bot_name):
        file_name = 'order_' + order_id + '_' + bot_name + '.png'
        try:
            self.driver.find_element(By.XPATH,
                                     '//button[text()="                Оплатить заказ                "]').click()
            sleep(2)
            self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
            sleep(2)
            svg = self.driver.find_element(By.XPATH, '//div[@class="qr-code__value"]')
            self.save_qr_code(svg, file_name)
            sleep(2)
            self.driver.find_element(By.CLASS_NAME, 'popup__close').click()
        except:
            file = open("/configs/configs.yaml").read()
            config = eval(file)
            Utils.login(self.driver, config['bots'][bot_name]['number'])
            self.get_qr_code(order_id, bot_name)

        return file_name

    def save_qr_code(self, svg, file_name):
        svg.screenshot(file_name)