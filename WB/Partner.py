from datetime import date, datetime, timedelta
from selenium.webdriver.common.by import By
import pickle
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait

from TG.Models.Orders import Orders
from WB.Browser import Browser


class Partner:
    def __init__(self, driver=False):
        self.browser = Browser(driver)
        self.driver = self.browser.driver

    def collect_orders(self):
        orders = self.get_not_collected_orders()
        print(len(orders))
        self.open()
        inns = []
        orders.sort(key=lambda x: x.inn)
        for order in orders:
            if order.inn not in inns:
                inns += [order.inn]
        for inn in inns:
            self.choose_inn(inn)
            self.open_marketplace()
            for order in orders:
                if order.inn == inn:
                    self.choose_task(order)
                else:
                    break

    def get_not_collected_orders(self):
        orders = Orders.load(collected=False)
        return orders

    def open(self):
        self.driver.get('https://seller.wildberries.ru/')
        cookies = pickle.load(open('./bots_sessions/Partner_1.pkl', "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.get('https://seller.wildberries.ru/')

    def choose_inn(self, inn):
        WebDriverWait(self.driver, 60).until(
            lambda d: d.find_element(By.XPATH, "//div[contains(@class,'DesktopProfileSelect')]/button")).click()
        self.driver.find_element(By.XPATH, f"//*[contains(text(),'ИНН {inn}')]").click()

    def open_marketplace(self):
        self.driver.find_element(By.XPATH, "//span[text()='Маркетплейс']/../../a").click()
        sleep(1)
        # marketplace = self.driver.find_element(By.XPATH,
        #                                        "//span[text()='Сборочные задания (везу на склад WB)']/../../a")
        # marketplace.click()

    def get_tasks(self):
        rows = self.driver.find_elements(By.XPATH, "//div[contains(@class,'row__')]")[1:]
        tasks = []
        for row in rows:
            link = row.find_element(By.XPATH, "./div/div/a")
            href = link.get_attribute('href')
            cat_i = href.index('catalog/')
            start_art = cat_i + len('catalog/')
            article = href[start_art:start_art + 8]

            date = row.find_element(By.XPATH,
                                    "./div[contains(@class,'creationDat')]/div/div/div[contains(@class,'date')]").text
            time = row.find_element(By.XPATH,
                                    "./div[contains(@class,'creationDat')]/div/div/div[contains(@class,'time')]").text
            dt = datetime.strptime(date + " " + time, "%d.%m.%Y %H:%M")

            delivery_address = row.find_element(By.XPATH, "./div[contains(@class,'deliveryAddress')]").text

            tasks += [{'date': date, 'time': time, 'datetime': dt, 'article': article, 'row': row,
                        'delivery_address': delivery_address}]

        return tasks

    def choose_task(self, order):
        tasks = self.get_tasks()
        print(tasks)
        for task in tasks:
            for i in range(len(order.articles)):
                if task['article'] == order.articles[i]:
                    _task_time = datetime.fromisoformat(str(task['datetime']))
                    order_time = datetime.fromisoformat(str(order.start_date))
                    print('times ', _task_time, order_time)
                    if abs(order_time - _task_time).seconds < 120 and task['delivery_address'] == order.pup_address:
                        WebDriverWait(task['row'], 60).until(
                            lambda d: d.find_element(By.XPATH, "./div/div/label")).click()
                        print(f'picked {order.articles[i]}, {order.pup_address}, {order.start_date}')

    def choose_tasks(self, orders):
        for order in orders:
            self.choose_task(order)

    def add_to_assembly(self):
        # Нажимаем кнопку принятия кукисов, если она еще на странице
        try:
            cookies_btn = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'WarningCookiesBannerCard__button')/button")
            cookies_btn.click()
            sleep(1)
        except:
            pass

        add_btn = WebDriverWait(self.driver, 60).until(
            lambda d: d.find_elements(By.XPATH, "//div[@class='New-tasks-table-row-view__33HSVACKTB']"))
        add_btn.click()

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
