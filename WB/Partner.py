from datetime import date, datetime, timedelta
from selenium.webdriver.common.by import By
import pickle
from time import sleep

from WB.Browser import Browser


class Partner:
    def __init__(self, driver=False):
        self.browser = Browser(driver)
        self.driver = self.browser.driver

    def open(self):
        self.driver.get('https://seller.wildberries.ru/')
        cookies = pickle.load(open('../bots_sessions/Parther.pkl', "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.get('https://seller.wildberries.ru/')

    def choose_inn(self, inn):
        self.driver.find_element(By.XPATH, "//div[contains(@class,'DesktopProfileSelect')]/button").click()
        self.driver.find_element(By.XPATH, f"//*[contains(text(),'ИНН {inn}')]").click()

    def open_marketplace(self):
        self.driver.find_element(By.XPATH, "//span[text()='Маркетплейс']/../../a").click()
        sleep(1)
        marketplace = self.driver.find_element(By.XPATH,
                                               "//span[text()='Сборочные задания (везу на склад WB)']/../../a")
        marketplace.click()

    def get_tasks(self):
        rows = self.driver.find_elements(By.XPATH, "//div[@class='New-tasks-table-row-view__33HSVACKTB']")
        orders = []
        for row in rows:
            link = row.find_element(By.XPATH, "./div/div[@class='New-tasks-table-row-view__cell-inner-content']/a")
            href = link.get_attribute('href')
            cat_i = href.index('catalog/')
            start_art = cat_i + len('catalog/')
            article = href[start_art:start_art + 8]

            date = row.find_element(By.XPATH,
                                    "./div[contains(@class,'creationDat')]/div/div/div[contains(@class,'date')]").text
            time = row.find_element(By.XPATH,
                                    "./div[contains(@class,'creationDat')]/div/div/div[contains(@class,'time')]").text
            dt = datetime.strptime(date + " " + time, "%d.%m.%Y %H:%M")
            orders += [{'date': date, 'time': time, 'datetime': dt, 'article': article, 'row': row}]

        return orders

    def choose_tasks(self, orders):
        tasks = self.get_tasks()
        for order in orders:
            for task in tasks:
                if task['article'] == order['article']:
                    _task_time = datetime.fromisoformat(str(task['datetime']))
                    task_time = datetime.fromisoformat(str(order['datetime']))
                    if abs(task_time - task_time).seconds < 120:

                        break

    def get_target_task(self, article, order_datetime):
        self.tasks = self.get_tasks()
        min_dif = timedelta(weeks=6)
        min_task = None
        for task in self.tasks:
            if task['article'] == article:
                _task_time = datetime.fromisoformat(str(task['datetime']))
                task_time = datetime.fromisoformat(str(order_datetime))
                dif = abs(task_time - task_time)
                if dif < min_dif:
                    min_dif = dif
                    min_task = task

        return min_task