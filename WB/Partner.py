from datetime import date, datetime, timedelta

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import pickle
from asyncio import sleep
import base64
from aiogram import Bot as TG_Bot

from selenium.webdriver.support.wait import WebDriverWait

from TG.Models.ExceptedOrders import ExceptedOrders
from TG.Models.Orders import Orders
from WB.Browser import Browser
from configs import config

API_TOKEN = config['tokens']['telegram']

class Partner:
    def __init__(self, driver=False):
        self.browser = Browser(driver)
        self.driver = self.browser.driver

    async def collect_orders(self):
        orders = await self.get_not_collected_orders()
        print(orders)
        inns = []
        orders.sort(key=lambda x: x.inn)
        for order in orders:
            if order.inn not in inns:
                inns += [order.inn]
        for inn in inns:
            await self.open(inn)
            await self.open_marketplace()
            await sleep(10)
            for order in orders:
                if order.inn == inn:
                    print(order)
                    await self.choose_task(order)
                else:
                    break
            await sleep(5)
            await self.add_to_assembly()
            await self.go_to_assembly()
            await self.create_assembly()
            await self.open_and_send_shks()
            await self.pick_all_tasks()
            await self.print_all_tasks_shk()
            await self.close_assembly()

    async def collect_other_orders(self, inn):
        await self.open(inn)
        await self.open_marketplace()
        await sleep(10)
        excepted_orders = ExceptedOrders.load(inn)
        excepted_orders_numbers = [eo.order_number for eo in excepted_orders]
        self.choose_all_tasks_except(excepted_orders_numbers)
        await sleep(5)
        # await self.add_to_assembly()
        # await self.go_to_assembly()
        # await self.create_assembly()
        # await self.open_and_send_shks()
        # await self.pick_all_tasks()
        # await self.print_all_tasks_shk()
        # await self.close_assembly()

    async def get_not_collected_orders(self):
        orders = Orders.load(collected=False)
        return orders

    async def open(self, inn):
        self.driver.get('https://seller.wildberries.ru/')
        cookies = pickle.load(open(f'./bots_sessions/Partner_{inn}.pkl', "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.get('https://seller.wildberries.ru/')

    async def choose_inn(self, inn):
        WebDriverWait(self.driver, 60).until(
            lambda d: d.find_element(By.XPATH, "//div[contains(@class,'DesktopProfileSelect')]/button")).click()
        self.driver.find_element(By.XPATH, f"//*[contains(text(),'ИНН {inn}')]").click()

    async def open_marketplace(self):
        marketplace_btn = WebDriverWait(self.driver, 60).until(
            lambda d: d.find_element(By.XPATH, "//span[text()='Маркетплейс']/../../a"))
        await sleep(2)
        marketplace_btn.click()
        # marketplace = self.driver.find_element(By.XPATH,
        #                                        "//span[text()='Сборочные задания (везу на склад WB)']/../../a")
        # marketplace.click()

    async def get_tasks(self):
        await sleep(2)
        rows = WebDriverWait(self.driver, 60).until(
            lambda d: d.find_elements(By.XPATH, "//div[contains(@class,'row__')]"))[1:]
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

    async def choose_task(self, order):
        """
        Выбирает товар на сборку, который по параметрам совпадает с переданныым в него заказом.
        Сравнивает заказ и товар в списке сборочных заданий
        по схожести артикула,
        приблизительно одинаковому времени
        и схожему адресу доставки.
        """
        tasks = await self.get_tasks()
        for i in range(len(order.articles)):
            for j, task in enumerate(tasks):
                if task['article'] == order.articles[i] and task['delivery_address'] == order.pup_address:
                    _task_time = datetime.fromisoformat(str(task['datetime']))
                    order_time = datetime.fromisoformat(str(order.start_date))
                    print('times ', _task_time, order_time)
                    if abs(order_time - _task_time).seconds < 120:
                        WebDriverWait(task['row'], 60).until(
                            lambda d: d.find_element(By.XPATH, "./div/div/label")).click()
                        print(f'picked {order.articles[i]}, {order.pup_address}, {order.start_date}')
                        break
                if j == len(tasks)-1:
                    print(f"Артикул {order.articles[i]} не найден")

    async def choose_tasks(self, orders):
        for order in orders:
            await self.choose_task(order)

    async def add_to_assembly(self):
        """
        Нажимаем кнопку "Собрать сборку"
        """
        # нажимаем кнопку принятия кукисов, если она еще на странице
        try:
            cookies_btn = self.driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'WarningCookiesBannerCard__button')]/button")
            cookies_btn.click()
            await sleep(1)
        except:
            print("cookies_btn not defined")
            pass
        
        await sleep(2)
        try:
            collect_btn = self.driver.find_element(By.XPATH, "//span[text()='Создать поставку']/..")
            collect_btn.click()
        except:
            try:
                print("Нет кнопки Создать поставку")
                collect_btn = self.driver.find_element(By.XPATH, "//span[text()='Добавить к сборке']/..")
                collect_btn.click()
            except:
                print("Нет кнопки Добавить в сборку")
        await sleep(1)

    async def go_to_assembly(self):
        on_assembly_tab = self.driver.find_element(By.XPATH, "//a[contains(text(),'На сборке')]")

        hover = ActionChains(self.driver)

        # resolve
        hover.move_to_element(on_assembly_tab).perform()
        on_assembly_tab.click()
        await sleep(1)

    async def create_assembly(self):
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.find_element(By.XPATH, "//span[text()='Создать поставку']/..").click()
        await sleep(2)
        self.driver.find_element(By.XPATH, "//span[text()='Готово']/..").click()
        await sleep(2)
        self.driver.find_element(By.XPATH, "//div[contains(@class, 'Modal__close')]/button").click()
        await sleep(2)

    async def get_target_task(self, article, order_datetime):
        self.tasks = self.get_tasks()
        min_dif = timedelta(weeks=6)
        min_task = None
        for task in await self.tasks:
            if task['article'] == article:
                task_time = datetime.fromisoformat(str(task['datetime']))
                order_time = datetime.fromisoformat(str(order_datetime))
                dif = abs(order_time - task_time)
                if dif < min_dif:
                    min_dif = dif
                    min_task = task
        
        return min_task

    async def pick_all_tasks(self):
        """
        Выбирает все сборочные задания
        """
        tasks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'Table-row__')]")
        for task in tasks:
            checkbox = task.find_element(By.XPATH, "./div/div/label")
            checkbox.click()

    async def open_and_send_shks(self):
        """
        Открывает все штрихкоды товаров и отправлет их в Фулфилмент
        Для использования этой функции нужно находиться на странице сборки товаров
        """
        # на всякий случай возвращаемся на первую вкладку
        await self.to_only_one_tab()

        # получаем бота для отправки сообщения от его имени
        bot = TG_Bot(token=API_TOKEN)

        # получаем список всех тасок
        tasks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'Table-row__')]")
        for task in tasks:
            self.driver.switch_to.window(self.driver.window_handles[0])

            # получаем артикул товара
            link = task.find_element(By.XPATH, "./div/div/a")
            href = link.get_attribute('href')
            cat_i = href.index('catalog/')
            start_art = cat_i + len('catalog/')
            article = href[start_art:start_art + 8]
            print("article", article)

            # открываем blob с артикулом в новой вкладке
            task.find_element(By.XPATH, "./div/div/button").click()
            await sleep(1)
            self.driver.find_element(By.XPATH, "//span[text()='Распечатать этикетку']").click()
            await sleep(1)
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # получаем байткод pdf файла и отправляем его на адрес Фулфилмента
            shk_bytes = self.get_file_content_chrome()
            await bot.send_document("794329884", (f'{article}.pdf', shk_bytes))
            await bot.send_document("791436094", (f'{article}.pdf', shk_bytes))
            await bot.send_document("424847668", (f'{article}.pdf', shk_bytes))
            await sleep(1)

            # закрываем таб с pdf файлом
            self.driver.close()

        # возвращаемся на первую вкладку
        await self.to_only_one_tab()

    async def get_file_content_chrome(self):
        result = self.driver.execute_async_script("""
            var uri = arguments[0];
            var callback = arguments[1];
            var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
            var xhr = new XMLHttpRequest();
            xhr.responseType = 'arraybuffer';
            xhr.onload = function(){ callback(toBase64(xhr.response)) };
            xhr.onerror = function(){ callback(xhr.status) };
            xhr.open('GET', uri);
            xhr.send();
            """, self.driver.current_url)
        if type(result) == int:
            raise Exception("Request failed with status %s" % result)
        return base64.b64decode(result)

    async def print_all_tasks_shk(self):
        # получаем бота для отправки сообщения от его имени
        bot = TG_Bot(token=API_TOKEN)

        # нажимаем кнопку "Распечатать этикетки и добавить товары в поставку" и подтверждаем это
        self.driver.find_element(By.XPATH,
                                    "//span[text()='Распечатать этикетки и добавить товары в поставку']/..").click()
        await sleep(2)
        self.driver.find_element(By.XPATH, "//span[@class='Button-link__text' and text()='Ок']").click()
        await sleep(2)

        # возвращаемся на первую вкладку
        await self.to_only_one_tab()

        # закрываем модалку, нажимаем на "Распечатать код поставка" и отправляем штрихкод на Фуллфилмент
        self.driver.find_element(By.XPATH, "//div[contains(@class, 'Modal__close')]/button").click()
        await sleep(1)
        tasks_shk = self.driver.find_element(By.XPATH, "//div[contains(@class,'All-tasks-view__shk')]").text
        self.driver.find_element(By.XPATH, "//span[text()='Распечатать']").click()
        await sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        shk_bytes = self.get_file_content_chrome()
        await bot.send_document("794329884", (f'{tasks_shk}.pdf', shk_bytes))
        await bot.send_document("791436094", (f'{tasks_shk}.pdf', shk_bytes))
        await bot.send_document("424847668", (f'{tasks_shk}.pdf', shk_bytes))
        await sleep(1)

        # возвращаемся на первую вкладку
        await self.to_only_one_tab()

    async def close_assembly(self):
        """
        Нажимает кнопку "Закрыть поставку"
        """
        self.driver.find_element(By.XPATH, "//span[text()='Закрыть поставку']").click()
        await sleep(1)

    async def to_only_one_tab(self):
        """
        Закрываем все вкладки, кроме первой
        """
        while len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            await sleep(1)
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
