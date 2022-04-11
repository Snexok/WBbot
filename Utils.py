from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from time import sleep
import random

CONTROL = Keys.CONTROL
DELETE = Keys.DELETE
ENTER = Keys.ENTER


class Utils():
    def __init__(self, browser) -> None:
        self.driver = browser.driver

    def login(self, number):
        # vars
        to_login_btn = self.driver.find_element(By.CLASS_NAME, 'j-main-login')
        login_input = self.driver.find_element(By.CLASS_NAME, 'input-item')
        login_btn = self.driver.find_element(By.CLASS_NAME, 'login__btn')

        # resolve
        to_login_btn.click()
        sleep(random.uniform(3, 5))
        login_input.send_keys(number)
        sleep(random.uniform(2, 4))
        login_btn.click()

    def search(self, key):
        # vars
        search_input = self.driver.find_element(By.ID, 'searchInput')

        # resolve
        search_input.click()
        search_input.send_keys(CONTROL + "a")
        search_input.send_keys(DELETE)
        search_input.send_keys(key)
        search_input.send_keys(ENTER)

    def go_to_basket(self):
        self.driver.find_element(By.CLASS_NAME, 'navbar-pc__icon--basket').click()
        return 'basket' #page
