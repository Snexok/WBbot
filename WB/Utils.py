from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from time import sleep
import random

from selenium.webdriver.support.wait import WebDriverWait

CONTROL = Keys.CONTROL
DELETE = Keys.DELETE
ENTER = Keys.ENTER


class Utils:

    # functions
    page_back = lambda self: self.driver.back()

    @staticmethod
    def login(driver, number):
        # vars # 1
        to_login_btn = driver.find_element(By.CLASS_NAME, 'j-main-login')

        # resolve # 1
        to_login_btn.click()
        sleep(random.uniform(3, 5))

        # vars # 2
        login_input = driver.find_element(By.CLASS_NAME, 'input-item')
        login_btn = driver.find_element(By.CLASS_NAME, 'login__btn')

        # resolve # 2
        login_input.send_keys(number)
        sleep(random.uniform(2, 4))
        login_btn.click()

        input("Требуется ручное действие")

    @staticmethod
    def search(driver, key):
        sleep(3)
        # vars
        search_input = WebDriverWait(driver, 60).until(
            lambda d: d.find_element(By.ID, 'searchInput'))

        # resolve
        search_input.click()
        search_input.send_keys(CONTROL + "a")
        search_input.send_keys(DELETE)
        search_input.send_keys(key)
        search_input.send_keys(ENTER)

        return 'catalog'

    @staticmethod
    def open_category(driver, key):
        sleep(3)
        hover = ActionChains(driver)


        key = key.split(";")

        category_menu_btn = WebDriverWait(driver, 60).until(
            lambda d: d.find_element(By.XPATH, '//button[contains(@class, "nav-element__burger")]'))

        sleep(1)
        category_menu_btn.click()

        for i, k in enumerate(key):
            sleep(1)
            category_btn = driver.find_element(By.XPATH, f'//*[text()="{k}"]')
            hover.move_to_element(category_btn).perform()
            if i == len(key)-1 or category_btn.tag_name == "span":
                category_btn.click()

        return 'catalog'


    @staticmethod
    def go_to_basket(driver):
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.CLASS_NAME, 'navbar-pc__icon--basket')).click()
        return 'basket' #page

    @staticmethod
    def get_basket_cnt(driver):
        basket = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.CLASS_NAME, 'navbar-pc__icon--basket'))
        return basket.text
