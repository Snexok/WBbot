def login(number):
    driver.find_element(By.CLASS_NAME, 'j-main-login').click()
    sleep(random.uniform(3,5))
    driver.find_element(By.CLASS_NAME, 'input-item').send_keys(number)
    sleep(random.uniform(2,4))
    driver.find_element(By.CLASS_NAME, 'login__btn').click()
    

     
def search(key):
    driver.find_element(By.ID, 'searchInput').click()
    driver.find_element(By.ID, 'searchInput').send_keys(key)
    driver.find_element(By.ID, 'searchInput').send_keys(Keys.ENTER)
    
def card_search(articul, scrolling=True, fake_choose=True): #Возвращает элемент страницы карточки товара
    hover = ActionChains(driver)
    card_finded = False
    scroll_step = 500
    while not card_finded:
        Y = 150
        card_cnt = 4

        cards = driver.find_elements(By.XPATH, '//div[contains(@class, "product-card j-card-item")]')
        for card in cards:
            print(card.get_attribute("id")[1:])
            if scrolling: # Каждые 4 провереных товара скролим экран
                if card_cnt == 4:
                    driver.execute_script("window.scrollTo({top: "+str(Y+random.randint(-20, 20))+",behavior: 'smooth'})")
                    sleep(random.uniform(1,5))
                    Y = Y+scroll_step
                    print(Y)
                    card_cnt = 0
                card_cnt += 1
            if fake_choose:
                if random.randint(1,10) == 8:
                    _articul = card.get_attribute("id")
                    img = driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/div/img')
                    hover.move_to_element(img).perform()
                    sleep(1.5)
                    card_button = driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/button')
                    card_button.click()
                    sleep(random.uniform(3,7))
#                     if random.randint(1,5) == 3:
                    if random.randint(1,3) == 3:
                        if random.randint(1,2) == 2:
                            see_images()
                        card_to_basket()
                        sleep(2.5)
                    sleep(random.uniform(2,5))
                    close_card_modal()
            # Проверяем товар по артиклу
            sleep(random.uniform(0,1))
            if card.get_attribute("id")[1:] == articul:
                _articul = card.get_attribute("id")
                img = driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/div/img')
                hover.move_to_element(img).perform()
                sleep(1.5)
                sleep(random.uniform(1,3))
                card_button = driver.find_element(By.XPATH, '//div[@id="'+ _articul +'"]/div/a/div/button')
                card_button.click()
                sleep(random.uniform(3,7))
                if random.randint(2,2) == 2:
                    see_images()
                card_to_basket()
                sleep(random.uniform(3,5))
                close_card_modal()
                return

        if not card_finded:
            next_page()
            sleep(2)
    
def next_page():
    driver.find_element(By.CLASS_NAME, 'pagination__next').click()
    
def close_card_modal():
    try:
        driver.find_element(By.CLASS_NAME, 'popup__close').click()
    except:
        page_back()
        sleep(2.5)
    
def see_images():
    hover = ActionChains(driver)

    for slide in driver.find_elements(By.CLASS_NAME, 'slide'):
        hover.move_to_element(slide).perform()
        sleep(random.uniform(1,5))
        if random.randint(1,4) == 3:
            return

def go_to_basket():
    driver.find_element(By.CLASS_NAME, 'navbar-pc__icon--basket').click()
    
def like():
    driver.find_element(By.CLASS_NAME, 'btn-heart').click()
    
def delete_other_cards_in_basket(articul):
    hover = ActionChains(driver)
    while True:
        card_names = driver.find_elements(By.XPATH, '//a[contains(@href, "catalog") and @class="good-info__title j-product-popup"]')
        card_name = card_names[random.choice(list(range(len(card_names))))]
        if card_name.get_attribute('href').find(articul) <= 0:
            counter = card_name.find_element(By.XPATH, '../../../div[contains(@class,"count")]')
            hover.move_to_element(counter).perform()
            sleep(random.uniform(1,5))
            counter.find_element(By.CLASS_NAME, 'btn__del').click()
        if len(card_names)<=1:
            return
            
def card_to_basket():
    try:
        basket_btn = driver.find_element(By.XPATH, '//span[contains(text(), "Добавить в корзину")]/..')
        if basket_btn:
#             size = driver.find_element(By.CLASS_NAME, 'j-size')
#             print('size', size)
#             if size:
#                 size.click()
            sleep(1)
            print('basket_btn', basket_btn)
            basket_btn.click()
    except:
        pass

def choose_post_place(adress):
    driver.find_element(By.XPATH, '//h2[text()="Способ доставки"]/../../div[text()="Выбрать адрес доставки"]').click()
    sleep(1)
    driver.find_element(By.XPATH, '//button[text()="Выбрать адрес доставки"]').click()
    sleep(2)
    driver.find_element(By.XPATH, '//input[@placeholder="Введите адрес"]').send_keys(adress)
    sleep(2)
    driver.find_element(By.XPATH, '//ymaps[text()="Найти"]').click()
    sleep(2)
    try:
        driver.find_element(By.XPATH, '//ymaps[contains(@class, "__first")]').click()
    except:
        pass
    sleep(2)
    driver.find_element(By.XPATH, '//span[contains(text(), "'+ adress +'")]').click()
    sleep(2)
    driver.find_element(By.XPATH, '//div[@class="balloon-content-block"]/button').click()
    sleep(2)
    driver.find_element(By.XPATH, '//button[@class="popup__btn-main"]').click()
    sleep(2)
    
def choose_payment_method(payment_method="Оплата по QR-коду"):
    driver.find_element(By.XPATH, '//h2[text()="Способ оплаты"]/../../div[text()="Выбрать способ оплаты"]').click()
    sleep(1)
    driver.find_element(By.XPATH, '//span[text()="' + payment_method + '"]').click()
    sleep(2)
    driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
    sleep(2)
    
def get_qr_code(file_name):
    driver.find_element(By.XPATH, '//button[text()="                Оплатить заказ                "]').click()
    sleep(2)
    driver.find_element(By.XPATH, '//button[contains(@class,"popup__btn-main")]').click()
    sleep(2)
    svg = driver.find_element(By.XPATH, '//div[@class="qr-code__value"]')
    save_qr_code(svg, file_name)
    sleep(2)
    driver.find_element(By.CLASS_NAME, 'popup__close').click()

def save_qr_code(svg, file_name):
    svg.screenshot(file_name)
    
def page_back():
    driver.back()
    
def main_page_surfing():
    pass 

def choose_filter_checkbox(filter_name,value):
    labels = driver.find_elements(By.XPATH, '//span[text()="'+filter_name+'" and contains(@class,"filter__name")]/../../div/fieldset/label')
    for label in labels:
        text = label.text
        text = text[:text.index("(")]
        text = text.strip()
        if text == value:
            label.click()
            break

def find_filter_checkbox(filter_name,value):
    search_field = driver.find_element(By.XPATH, '//span[text()="'+filter_name+'" and contains(@class,"filter__name")]/../../div/div/input')
    search_field.click()
    search_field.send_keys(value)
    sleep(1)
    choose_filter_checkbox(filter_name,value)
    
def price_filter(min_price, max_price):
    min_price_field = driver.find_element(By.XPATH, '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="startN"]')
    max_price_field = driver.find_element(By.XPATH, '//span[text()="Цена, ₽" and contains(@class,"filter__name")]/../../div/div/div/div/div/input[@name="endN"]') 
    min_price_field.click() 
    min_price_field.send_keys(Keys.CONTROL + "a") 
    min_price_field.send_keys(Keys.DELETE)
    min_price_field.send_keys(min_price)
    max_price_field.click
    max_price_field.send_keys(Keys.CONTROL + "a")
    max_price_field.send_keys(Keys.DELETE)
    max_price_field.send_keys(max_price)
