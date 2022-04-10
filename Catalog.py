from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random

Y = 150
SCROLL_STEP = 500

class Catalog():
    def __init__(self, driver) -> None:
        self.driver = driver

    # simple deempl
    min_price_field = lambda self: self.driver.find_element(By.XPATH, '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="startN"]')
    max_price_field = lambda self: self.driver.find_element(By.XPATH, '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="endN"]') 
    search_field = lambda self, filter_name: self.driver.find_element(By.XPATH, '//span[text()="'+filter_name+'" and contains(@class,"filter__name")]/../../div/div/input')
    card_button = lambda self, articul: self.driver.find_element(By.XPATH, '//div[@id="'+ articul +'"]/div/a/div/button')
    basket_btn = lambda self: self.driver.find_element(By.XPATH, '//span[contains(text(), "Добавить в корзину")]/..')
    page_back = lambda self: self.driver.back()
    next_page = lambda self: self.driver.find_element(By.CLASS_NAME, 'pagination__next').click()
    get_cards = lambda self: self.driver.find_elements(By.XPATH, '//div[contains(@class, "product-card j-card-item")]')
    like = lambda self: self.driver.find_element(By.CLASS_NAME, 'btn-heart').click()

    def card_search(self, articuls, scrolling=True, fake_choose=True):
        # data transform
        map(str, list(articuls))

        # resolve
        while True:
            card_cnt = 0

            cards = self.get_cards()
            for card in cards:
                sleep(random.uniform(0,1))

                articul = card.get_attribute("id")

                if scrolling:
                    self.scroll(card_cnt)
                if articul[1:] in articuls:
                    self.add_card(articul, target=True)
                elif fake_choose:
                    self.add_card(articul, target=False)

            self.next_page()
            sleep(2)


    def scroll(self, card_cnt):
        if card_cnt == 0:
            self.driver.execute_script("window.scrollTo({top: "+str(Y+random.randint(-20, 20))+",behavior: 'smooth'})")
            sleep(1)
            Y = Y+SCROLL_STEP
            card_cnt = 4
        card_cnt -= 1

    def choose_filter_checkbox(self, filter_name,value):
        labels = self.driver.find_elements(By.XPATH, '//span[text()="'+filter_name+'" and contains(@class,"filter__name")]/../../div/fieldset/label')
        for label in labels:
            text = label.text
            text = text[:text.index("(")]
            text = text.strip()
            if text == value:
                label.click()
                break

    def find_filter_checkbox(self, filter_name,value):
        search_field = search_field(filter_name)
        search_field.click()
        search_field.send_keys(value)
        sleep(1)
        self.choose_filter_checkbox(filter_name,value)
        
    def price_filter(self, min_price, max_price):
        min_price_field = min_price_field()
        min_price_field.click() 
        min_price_field.send_keys(Keys.CONTROL + "a") 
        min_price_field.send_keys(Keys.DELETE)
        min_price_field.send_keys(min_price)

        max_price_field = max_price_field()
        max_price_field.click()
        max_price_field.send_keys(Keys.CONTROL + "a")
        max_price_field.send_keys(Keys.DELETE)
        max_price_field.send_keys(max_price)

    def add_card(self, articul, target=False):
        img = self.driver.find_element(By.XPATH, '//div[@id="'+ articul +'"]/div/a/div/div/img')
        hover = ActionChains(self.driver)
        hover.move_to_element(img).perform()

        sleep(random.uniform(2,4))
        self.card_button(articul).click()


        if target:
            sleep(random.uniform(3,7))
            if random.randint(1,2) == 2:
                self.see_images()
            self.card_to_basket()
        else:
            sleep(random.uniform(1,5))
            if random.randint(1,20) == 3:
                if random.randint(1,3) == 2:
                    self.see_images()
                self.card_to_basket()
                sleep(2.5)
        sleep(random.uniform(3,5))
        self.close_card_modal()
        
        del hover

    def card_to_basket(self):
        try:
            self.basket_btn().click()
        except:
            pass
        
    def close_card_modal(self):
        try:
            self.driver.find_element(By.CLASS_NAME, 'popup__close').click()
        except:
            self.page_back()
            sleep(2.5)
        
    def see_images(self):
        hover = ActionChains(self.driver)

        for slide in self.driver.find_elements(By.CLASS_NAME, 'slide'):
            hover.move_to_element(slide).perform()
            sleep(random.uniform(1,5))
            if random.randint(1,4) == 3:
                return
        