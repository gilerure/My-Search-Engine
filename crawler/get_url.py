import re
import os
def getURL():
    with open('url.txt', 'w', encoding='utf-8'):
        pass
    for filename in os.listdir('result'):
        path1 = os.path.join('result', filename)
        with open(path1, 'r', encoding='utf-8') as file:
            content = file.read()
        product_url_match = re.search(r'Product URL: (.+)', content)
        if product_url_match:
            product_url = product_url_match.group(1)
            with open('url.txt', 'a', encoding='utf-8') as file:
                file.write(product_url)
                file.write('\n')
getURL()