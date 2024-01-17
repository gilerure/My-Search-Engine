from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import urllib
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import string
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# 得到合法的文件名
def valid_filename(s, max_length=60):    
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)[:max_length]
    
    return s

def scrape_page(driver):
    # 模拟滚动，加载更多的商品
    for i in range(5): 
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2) 

    # 获取完整的页面内容
    page_source = driver.page_source

    # 使用 BeautifulSoup 解析页面内容
    soup = BeautifulSoup(page_source, 'html.parser')

    # 提取标题、图片和超链接信息
    items = soup.find_all('div', class_='Card--mainPicAndDesc--wvcDXaK')

    # 使用列表存储标题、图片和超链接的对应关系
    title_image_url_list = []

    for item in items:
        title_text = item.find('div', class_='Title--title--jCOPvpf').find('span').text.strip() if item.find('div', class_='Title--title--jCOPvpf') else ''
        image_url = item.find('div', class_='MainPic--mainPicWrapper--iv9Yv90').find('img')['src'].strip() if item.find('div', class_='MainPic--mainPicWrapper--iv9Yv90') and item.find('div', class_='MainPic--mainPicWrapper--iv9Yv90').find('img') else ''
        href = item.find_previous('a', class_='Card--doubleCardWrapper--L2XFE73')['href'].strip() if item.find_previous('a', class_='Card--doubleCardWrapper--L2XFE73') else ''
        price = item.find('div', class_='Price--priceWrapper--Q0Dn7pN').find('span', class_='Price--unit--VNGKLAP').text.strip() + item.find('div', class_='Price--priceWrapper--Q0Dn7pN').find('span', class_='Price--priceInt--ZlsSi_M').text.strip() + item.find('div', class_='Price--priceWrapper--Q0Dn7pN').find('span', class_='Price--priceFloat--h2RR0RK').text.strip()
        href = urllib.parse.urljoin(url, href)
        # 存储到列表
        title_image_url_list.append((title_text, image_url, price, href))

    return title_image_url_list

def main():
    global keyword, url
    keyword = '优衣库'
    url = f'https://s.taobao.com/search?q={urllib.parse.quote(keyword)}'
    brand = urllib.parse.unquote(keyword)

    chrome_driver_path = 'C:\\Users\\25458\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
    chrome_options = ChromeOptions()
    
    # 设置 ChromeOptions
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 关闭自动测试状态
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument('--headless')

    driver=webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    wait = WebDriverWait(driver,10)
    driver.get(url)
    time.sleep(30)
   

    try:
        # 爬取第一页
        title_image_url_list = scrape_page(driver)

        # 写入文件
        for title, image_url, price, href in title_image_url_list:
            try:
                validname = valid_filename(href)
                with open(f'result/{validname}.txt', 'w', encoding='utf-8') as file:
                    # Write to the file
                    file.write(f'Title: {title}\n')
                    file.write(f'Image URL: {image_url}\n')
                    file.write(f'Brand: {brand}\n')
                    file.write(f'Price: {price}\n')
                    file.write(f'Product URL: {href}\n')
                    file.write('\n')
            except Exception as err:
                continue

        # 模拟点击加载更多页，可以调整页码的范围
        for page in range(2, 50): 
            next_page_button = driver.find_element(By.CLASS_NAME, 'next-next')
            ActionChains(driver).move_to_element(next_page_button).click().perform()

            # 等待加载完成
            time.sleep(8)

            # 爬取当前页
            title_image_url_list = scrape_page(driver)

            # 写入文件
            for title, image_url, price, href in title_image_url_list:
                validname = valid_filename(href)
                try:
                    with open(f'result/{validname}.txt', 'w', encoding='utf-8') as file:
                        file.write(f'Title: {title}\n')
                        file.write(f'Image URL: {image_url}\n')
                        file.write(f'Brand: {brand}\n')
                        file.write(f'Price: {price}\n')
                        file.write(f'Product URL: {href}\n')
                        file.write('\n')
                except Exception as err:
                    continue

    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    main()
