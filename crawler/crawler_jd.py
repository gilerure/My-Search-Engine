from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import time
import string
#提供合适的文件名称
def valid_filename(s, max_length=60):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)[:max_length]
    return s
# 等待对应的元素出现
def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

# 模拟真实用户点击对应的元素
def scroll_to_element(driver, element):
    ActionChains(driver).move_to_element(element).perform()

# 爬取主要的页面信息
def scrape_page(driver):
    time.sleep(5)#将程序休眠，应对反爬虫的检测
    wait_for_element(driver, By.CLASS_NAME, 'gl-warp')
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    items = soup.find_all('li', class_='gl-item')

    data_list = []#这个列表中存该页面中所有的商品信息，包括标题，图片url，价格，商品链接

    for item in items:
        try:
            title_text = item.find('div', class_='p-name').find('em').text.strip() if item.find('div', class_='p-name') else ''
            image_url = item.find('div', class_='p-img').find('img')['src'].strip() if item.find('div', class_='p-img') and item.find('div', class_='p-img').find('img') else ''
            href = item.find('div', class_='p-name').find('a')['href'].strip() if item.find('div', class_='p-name') and item.find('div', class_='p-name').find('a') else ''
            price = item.find('div', class_='p-price').find('i').text.strip()
            href = urllib.parse.urljoin(url, href)
            image_url = urllib.parse.urljoin(url, image_url)
            data_list.append({
                'title': title_text,
                'image_url': image_url,
                'price': price,
                'href': href
            })
        except Exception as err:
            continue

    return data_list

def main():
    global keyword, url
    keyword = '吉普（JEEP）'
    searchfor = '服装'
    url = f'https://search.jd.com/search?keyword={urllib.parse.quote(searchfor)}&wq={urllib.parse.quote(searchfor)}&ev=exbrand_{urllib.parse.quote(keyword)}%5E'
    # url = 'https://search.jd.com/Search?keyword=%E4%B8%AD%E5%9B%BD%E6%9D%8E%E5%AE%81%E6%97%97%E8%88%B0%E5%BA%97%E5%86%AC%E8%A3%85&enc=utf-8&wq=%E4%B8%AD%E5%9B%BD%E6%9D%8E%E5%AE%81%E6%97%97%E8%88%B0%E5%BA%97dong%27zhuang&pvid=b1ce18ee8d7544e490e0179f029ee09b'
    brand = urllib.parse.unquote(keyword)

    
    chrome_driver_path = 'C:\\Users\\25458\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'#这个路径是我chrome_driver所在的路径
    chrome_options = ChromeOptions()
    # 这一部分将自动检测关闭，以保证爬虫的正常进行
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    # wait = WebDriverWait(driver, 10)
    # wait = WebDriverWait(driver, 10)
    driver.get(url)
    #留响应的时间，应对反爬虫或者说未得到对应url响应的问题
    time.sleep(15)

    try:
        data_list = scrape_page(driver)

        for data in data_list:
            try:
                #将有关信息存储到txt文件当中
                validname = valid_filename(data['href'])
                with open(f'result/{validname}.txt', 'w', encoding='utf-8') as file:
                    file.write(f'Title: {data["title"]}\n')
                    file.write(f'Image URL: {data["image_url"]}\n')
                    file.write(f'Brand: {brand}\n')
                    file.write(f'Price: {data["price"]}\n')
                    file.write(f'Product URL: {data["href"]}\n')
                    file.write('\n')
            except Exception as err:
                continue
        #调整这个数字可以选择爬取的页面范围
        for page in range(2, 100):
            #加入try except防止一些报错的影响爬虫正常进行
            try:
                
                next_page_button = wait_for_element(driver, By.CLASS_NAME, 'pn-next')
                # 模拟用户鼠标滑到对应的下一页按钮上
                scroll_to_element(driver, next_page_button)
                time.sleep(2)
                #实行点击下一页的按钮
                next_page_button.click()
                time.sleep(3)
                #等待对应元素的出现
                driver.refresh()
                wait_for_element(driver, By.CLASS_NAME, 'gl-warp')

                data_list = scrape_page(driver)

                for data in data_list:
                    validname = valid_filename(data['href'])
                    try:
                        with open(f'result/{validname}.txt', 'w', encoding='utf-8') as file:
                            file.write(f'Title: {data["title"]}\n')
                            file.write(f'Image URL: {data["image_url"]}\n')
                            file.write(f'Brand: {brand}\n')
                            file.write(f'Price: {data["price"]}\n')
                            file.write(f'Product URL: {data["href"]}\n')
                            file.write('\n')
                    except Exception as err:
                        continue
            except Exception:
                continue

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
