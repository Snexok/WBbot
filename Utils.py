from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from time import sleep
import random

CONTROL = Keys.CONTROL
DELETE = Keys.DELETE
ENTER = Keys.ENTER


class Utils:

    # functions
    page_back = lambda self: self.driver.back()

    @staticmethod
    def login(driver, number):
        # vars
        to_login_btn = driver.find_element(By.CLASS_NAME, 'j-main-login')
        login_input = driver.find_element(By.CLASS_NAME, 'input-item')
        login_btn = driver.find_element(By.CLASS_NAME, 'login__btn')

        # resolve
        to_login_btn.click()
        sleep(random.uniform(3, 5))
        login_input.send_keys(number)
        sleep(random.uniform(2, 4))
        login_btn.click()

    @staticmethod
    def search(driver, key):
        # vars
        search_input = driver.find_element(By.ID, 'searchInput')

        # resolve
        search_input.click()
        search_input.send_keys(CONTROL + "a")
        search_input.send_keys(DELETE)
        search_input.send_keys(key)
        search_input.send_keys(ENTER)

        return 'catalog'

    @staticmethod
    def go_to_basket(driver):
        driver.find_element(By.CLASS_NAME, 'navbar-pc__icon--basket').click()
        return 'basket' #page

    @staticmethod
    def close_card_modal(driver):
        try:
            driver.find_element(By.CLASS_NAME, 'popup__close').click()
        except:
            Utils.page_back(driver)
            sleep(2.5)
