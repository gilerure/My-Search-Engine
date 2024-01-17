from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import string
import re
import os
import time
import threading
import queue

chrome_driver_path = 'C:\\Users\\25458\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
chrome_options = ChromeOptions()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
# 根据url提供符合命名规则的文件名
def valid_filename(s, max_length=60):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)[:max_length]
    return s

# 得到好评率信息
def get_fav_rate(driver, url):
    for i in range(2):  
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(5)  
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    element = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "percent-con"))
    )
    fav_rate = soup.find('div', class_='percent-con')
    validname = valid_filename(url)
    with open(f'comment/{validname}.txt', 'w', encoding='utf-8') as file:
        file.write(f'好评率：{fav_rate.text}\n')

# 爬取一页中所有的评论信息
def scrape_page(driver, url):
    for i in range(1):  
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(3)

    element = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "comment-con"))
    )

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    comments = soup.find_all('p', class_='comment-con')

    for comment in comments:
        validname = valid_filename(url)
        with open(f'comment/{validname}.txt', 'a', encoding='utf-8') as file:
            file.write(f'{comment.text.strip()}\n')

# 每一个线程爬取一定页数的评论
def worker():
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    while True:
        try:
            url = url_queue.get()
            if url is None:
                break
            driver.get(url)
            get_fav_rate(driver,url)
            scrape_page(driver,url)
            for page in range(2, 11):  # 限制爬取的页数
                try:
                    next_page_button = driver.find_element(By.CLASS_NAME,'ui-pager-next')
                    ActionChains(driver).move_to_element(next_page_button).perform()
                    time.sleep(2)
                    next_page_button.click()
                    scrape_page(driver,url)
                except Exception as err:
                    continue
            url_queue.task_done()
        except:
            continue

def getURL(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = file.readlines()
    return [url.strip() for url in urls]

url_queue = queue.Queue()

# 加入URL到队列
for url in getURL('url.txt'):
    url_queue.put(url)

# 创建线程池
with ThreadPoolExecutor(max_workers=1) as executor:
    # 启动线程
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    # 等待队列中的所有任务完成
    url_queue.join()

    # 停止线程
    for _ in range(5):
        url_queue.put(None)
    for thread in threads:
        thread.join()

    # driver.quit()
