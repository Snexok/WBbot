from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random
import json

class Bot:
    def __init__(self, driver=False):
        if driver == False:
            self.driver = webdriver.Chrome("./chrome/chromedriver.exe")
        else:
            self.driver=driver

    def open_browser(self):
        self.driver = webdriver.Chrome("./chrome/chromedriver.exe")

    def open(self, site):
        self.driver.get(site)

    def login(self, number):
        self.driver.find_element(By.CLASS_NAME, 'j-main-login').click()
        sleep(random.uniform(3,5))
        self.driver.find_element(By.CLASS_NAME, 'input-item').send_keys(number)
        sleep(random.uniform(2,4))
        self.driver.find_element(By.CLASS_NAME, 'login__btn').click()

    def search(self, key):
        self.driver.find_element(By.ID, 'searchInput').click()
        self.driver.find_element(By.ID, 'searchInput').send_keys(Keys.CONTROL + "a") 
        self.driver.find_element(By.ID, 'searchInput').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'searchInput').send_keys(key)
        self.driver.find_element(By.ID, 'searchInput').send_keys(Keys.ENTER)
        
    def card_search(self, articul, scrolling=True, fake_choose=True): #Возвращает элемент страницы карточки товара
        hover = ActionChains(self.driver)
        card_finded = False
        scroll_step = 500
        articul = str(articul)
        while not card_finded:
            Y = 150
            card_cnt = 4

            cards = self.driver.find_elements(By.XPATH, '//div[contains(@class, "product-card j-card-item")]')
            for card in cards:
                if card.get_attribute("id")[1:] == articul:
                    print('card in page')
            for card in cards:
                # Проверяем товар по артиклу
                sleep(random.uniform(0,1))
                print(card.get_attribute("id")[1:])
                if card.get_attribute("id")[1:] == articul:
                    _articul = card.get_attribute("id")
                    img = self.driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/div/img')
                    hover.move_to_element(img).perform()
                    sleep(1.5)
                    sleep(random.uniform(1,3))
                    card_button = self.driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/button')
                    card_button.click()
                    sleep(random.uniform(3,7))
                    if random.randint(2,2) == 2:
                        self.see_images()
                    self.card_to_basket()
                    sleep(random.uniform(3,5))
                    self.close_card_modal()
                    return
                if scrolling: # Каждые 4 провереных товара скролим экран
                    if card_cnt == 4:
                        self.driver.execute_script("window.scrollTo({top: "+str(Y+random.randint(-20, 20))+",behavior: 'smooth'})")
                        sleep(1)
                        Y = Y+scroll_step
                        card_cnt = 0
                    card_cnt += 1
                if fake_choose:
                    if random.randint(1,10) == 8:
                        _articul = card.get_attribute("id")
                        img = self.driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/div/img')
                        hover.move_to_element(img).perform()
                        sleep(1)
                        card_button = self.driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/button')
                        card_button.click()
                        sleep(random.uniform(1,5))
    #                     if random.randint(1,5) == 3:
                        if random.randint(1,20) == 3:
                            if random.randint(1,3) == 2:
                                self.see_images()
                            self.card_to_basket()
                            sleep(2.5)
                        sleep(random.uniform(1,3))
                        self.close_card_modal()

            if not card_finded:
                self.next_page()
                sleep(2)
        
    def next_page(self):
        self.driver.find_element(By.CLASS_NAME, 'pagination__next').click()
        
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

    def go_to_basket(self):
        self.driver.find_element(By.CLASS_NAME, 'navbar-pc__icon--basket').click()
        
    def like(self):
        self.driver.find_element(By.CLASS_NAME, 'btn-heart').click()

    # Рефакторинг под множество артикулов
    def delete_other_cards_in_basket(self, articles):
        hover = ActionChains(self.driver)
        while True:
            card_names = self.driver.find_elements(By.XPATH, '//a[contains(@href, "catalog") and @class="good-info__title j-product-popup"]')
            card_name = card_names[random.choice(list(range(len(card_names))))]
            card_name_href = card_name.get_attribute('href')
            if not any(a in card_name_href for a in articles):
                counter = card_name.find_element(By.XPATH, '../../../div[contains(@class,"count")]')
                hover.move_to_element(counter).perform()
                sleep(random.uniform(1,5))
                counter.find_element(By.CLASS_NAME, 'btn__del').click()
            if len(card_names)<=len(articles):
                return
                
    def card_to_basket(self):
        try:
            basket_btn = self.driver.find_element(By.XPATH, '//span[contains(text(), "Добавить в корзину")]/..')
            if basket_btn:
    #             size = self.driver.find_element(By.CLASS_NAME, 'j-size')
    #             print('size', size)
    #             if size:
    #                 size.click()
                sleep(1)
                print('basket_btn', basket_btn)
                basket_btn.click()
        except:
            pass

    def choose_post_place(self, adress):
        self.driver.find_element(By.XPATH, '//h2[text()="Способ доставки"]/../../div[text()="Выбрать адрес доставки"]').click()
        sleep(1)
        self.driver.find_element(By.XPATH, '//button[text()="Выбрать адрес доставки"]').click()
        sleep(2)
        self.driver.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]').send_keys(adress)
        sleep(2)
        self.driver.find_element(By.XPATH, '//ymaps[text()="Найти"]').click()
        sleep(2)
        try:
            self.driver.find_element(By.XPATH, '//ymaps[contains(@class, "__first")]').click()
        except:
            pass
        sleep(2)
        self.driver.find_element(By.XPATH, '//span[contains(text(), "'+ adress +'")]').click()
        sleep(2)
        self.driver.find_element(By.XPATH, '//div[@class="balloon-content-block"]/button').click()
        sleep(2)
        self.driver.find_element(By.XPATH, '//button[@class="popup__btn-main"]').click()
        sleep(2)
        
    def choose_payment_method(self, payment_method="Оплата по QR-коду"):
        self.driver.find_element(By.XPATH, '//h2[text()="Способ оплаты"]/../../div[text()="Выбрать способ оплаты"]').click()
        sleep(1)
        self.driver.find_element(By.XPATH, '//span[text()="' + payment_method + '"]').click()
        sleep(2)
        self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
        sleep(2)
        
    def get_qr_code(self, file_name):
        self.driver.find_element(By.XPATH, '//button[text()="                Оплатить заказ                "]').click()
        sleep(2)
        self.driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
        sleep(2)
        svg = self.driver.find_element(By.XPATH, '//div[@class="qr-code__value"]')
        save_qr_code(svg, file_name)
        sleep(2)
        self.driver.find_element(By.CLASS_NAME, 'popup__close').click()

    def save_qr_code(self, svg, file_name):
        svg.screenshot(file_name)
        
    def page_back(self):
        self.driver.back()
        
    def main_page_surfing(self):
        pass 

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
        search_field = self.driver.find_element(By.XPATH, '//span[text()="'+filter_name+'" and contains(@class,"filter__name")]/../../div/div/input')
        search_field.click()
        search_field.send_keys(value)
        sleep(1)
        self.choose_filter_checkbox(filter_name,value)
        
    def price_filter(self, min_price, max_price):
        min_price_field = self.driver.find_element(By.XPATH, '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="startN"]')
        max_price_field = self.driver.find_element(By.XPATH, '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="endN"]') 
        min_price_field.click() 
        min_price_field.send_keys(Keys.CONTROL + "a") 
        min_price_field.send_keys(Keys.DELETE)
        min_price_field.send_keys(min_price)
        max_price_field.click
        max_price_field.send_keys(Keys.CONTROL + "a")
        max_price_field.send_keys(Keys.DELETE)
        max_price_field.send_keys(max_price)

    def get_data_cart(self, articul, SAVE=False):
        self.driver.get("https://www.wildberries.ru/")
        sleep(2)
        self.driver.get("https://www.wildberries.ru/catalog/"+articul+"/detail.aspx?targetUrl=MI")

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
            self.driver.find_element(By.XPATH, '//button[contains(@class, "collapsible__toggle") and text()="Развернуть описание"]').click()
        except:
            pass
        try:
            self.driver.find_element(By.XPATH, '//button[contains(@class, "collapsible__toggle") and text()="Развернуть характеристики"]').click()
        except:
            pass
        try:
            descriptions = self.driver.find_elements(By.XPATH, '//h2[contains(@class, "section-header") and text()="Описание"]/../../div')

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
                characters+=_characters
            data['characters'] = characters
        except:
            pass
        try:
            composition = self.driver.find_element(By.XPATH, '//h2[contains(@class, "section-header") and text()="Состав"]/../div/div').text
            if composition:
                data['composition'] = composition
        except:
            pass

        if SAVE:
            with open('card_data/'+articul+'.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        else:
            return data

    def buy(self, search_name, articul_num, post_place):
        self.search(search_name)
        sleep(2)
        self.card_search(articul_num)
        self.go_to_basket()
        sleep(1)
        self.delete_other_cards_in_basket(articul_num)
        sleep(3)
        self.choose_post_place(post_place)
        self.choose_payment_method()
        self.get_qr_code('order_'+articul_num+'.png')
