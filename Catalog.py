from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random
from Utils import Utils

from selenium.webdriver.support.wait import WebDriverWait

SCROLL_STEP = 500
SPEED = 0 # 1 << 0

class Catalog():
    def __init__(self, browser) -> None:
        self.driver = browser.driver
        self.Y = 150

    # simple deempl
    min_price_field = lambda self: self.driver.find_element(By.XPATH,
                                                            '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="startN"]')
    max_price_field = lambda self: self.driver.find_element(By.XPATH,
                                                            '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="endN"]')
    search_field = lambda self, filter_name: self.driver.find_element(By.XPATH,
                                                                      '//span[text()="' + filter_name + '" and contains(@class,"filter__name")]/../../div/div/input')
    card_button = lambda self, articul: self.driver.find_element(By.XPATH,
                                                                 '//div[@id="' + articul + '"]/div/a/div/button')
    basket_btn = lambda self: self.driver.find_element(By.XPATH, '//span[contains(text(), "Добавить в корзину")]/..')
    next_page = lambda self: self.driver.find_element(By.CLASS_NAME, 'pagination__next').click()
    get_cards = lambda self: self.driver.find_elements(By.XPATH, '//div[contains(@class, "product-card j-card-item")]')
    like = lambda self: self.driver.find_element(By.CLASS_NAME, 'btn-heart').click()
    get_sort_by = lambda self, filter: self.driver.find_element(By.XPATH,
                                                                '//div[@class="sort"]/a/span[text()="' + filter + '"]')

    def card_search(self, articles, scrolling=True, fake_choose=True):
        # data transform
        articles = list(map(str, articles if type(articles) == list else [articles]))

        # vars
        cnt = 0

        # resolve
        while True:
            card_cnt_for_scroll = 0
            self.Y = 150

            sleep(2)
            cards = self.get_cards()
            for card in cards:
                sleep(SPEED*random.uniform(0, 1))

                article = card.get_attribute("id")
                print(article, articles)
                if scrolling:
                    card_cnt_for_scroll = self.scroll(card_cnt_for_scroll)
                if article[1:] in articles:
                    self.add_card(article, target=True)

                    cnt += 1
                    if cnt >= len(articles):
                        return
                elif fake_choose:
                    if random.randint(0,5) == 3:
                        self.add_card(article, target=False)

            self.next_page()
            sleep(2)

    def scroll(self, card_cnt):
        if card_cnt == 0:
            self.driver.execute_script(
                "window.scrollTo({top: " + str(self.Y + random.randint(-20, 20)) + ",behavior: 'smooth'})")
            sleep(1)
            self.Y = self.Y + SCROLL_STEP
            card_cnt = 4
        return card_cnt - 1

    def choose_filter_checkbox(self, filter_name, value):
        labels = self.driver.find_elements(By.XPATH,
                                           '//span[text()="' + filter_name + '" and contains(@class,"filter__name")]/../../div/fieldset/label')
        for label in labels:
            text = label.text
            text = text[:text.index("(")]
            text = text.strip()
            if text == value:
                label.click()
                break

    def find_filter_checkbox(self, filter_name, value):
        search_field = self.search_field(filter_name)
        search_field.click()
        search_field.send_keys(value)
        sleep(1)
        self.choose_filter_checkbox(filter_name, value)

    def price_filter(self, min_price, max_price):
        min_price_field = self.min_price_field()
        min_price_field.click()
        min_price_field.send_keys(Keys.CONTROL + "a")
        min_price_field.send_keys(Keys.DELETE)
        min_price_field.send_keys(min_price)

        max_price_field = self.max_price_field()
        max_price_field.click()
        max_price_field.send_keys(Keys.CONTROL + "a")
        max_price_field.send_keys(Keys.DELETE)
        max_price_field.send_keys(max_price)

    def sort_by(self, filter, double_click=False):
        sort_el = self.get_sort_by(filter)
        sort_el.click()
        if double_click:
            sort_el.click()

    def card_to_basket(self):
        try:
            self.basket_btn().click()
        except:
            pass

    def add_card(self, articul, target=False):
        # vars
        img = self.driver.find_element(By.XPATH, '//div[@id="' + articul + '"]/div/a/div/div/img')
        hover = ActionChains(self.driver)

        # resolve
        hover.move_to_element(img).perform()

        sleep(SPEED*random.uniform(2, 4)+1)
        self.card_button(articul).click()
        sleep(1)
        if target:
            sleep(SPEED*random.uniform(3, 7))
            if random.randint(1, 2) == 2:
                self.see_images()
            self.card_to_basket()
        else:
            sleep(SPEED*random.uniform(1, 5))
            if random.randint(1, 20) == 3:
                if random.randint(1, 3) == 2:
                    self.see_images()
                self.card_to_basket()
                sleep(SPEED*2.5)
        sleep(SPEED*random.uniform(3, 5))
        Utils.close_card_modal(self.driver)

        del hover

    def see_images(self):
        hover = ActionChains(self.driver)

        for slide in self.driver.find_elements(By.CLASS_NAME, 'slide'):
            hover.move_to_element(slide).perform()
            sleep(SPEED*random.uniform(1, 5))
            if random.randint(1, 4) == 3:
                return
