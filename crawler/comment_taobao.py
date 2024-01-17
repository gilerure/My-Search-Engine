import requests
import re
import string
import json
def valid_filename(s, max_length=60):
    # 有效字符集合
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    
    # 只保留有效字符，并截断到指定的最大长度
    s = ''.join(c for c in s if c in valid_chars)[:max_length]
    
    return s

cookies = {
    '_samesite_flag_': 'true',
    'cookie2': '17b7a71bdd2fdaf129ba6f5be4886894',
    't': '6bc3a374ef61e40a3ef3eb14df43eabb',
    '_tb_token_': 'ee5196f01e777',
    'thw': 'cn',
    '_m_h5_tk': 'd81f72cb37588a9acad44a1b43328ebe_1702954754360',
    '_m_h5_tk_enc': '6859e95c3da50863a38af2dc676f7751',
    'sgcookie': 'E100EL2KKzTKwN71OEM772d3ZoebzxD%2FIHv7nuEAJQAzdiCuvQRIGxY6tIjteDZIKjjxoSBuA%2B0sS5CqXvOxyDXK2FxJpZ2SF2vQKRtEryq30wI%3D',
    'unb': '2217096635575',
    'uc3': 'lg2=V32FPkk%2Fw0dUvg%3D%3D&vt3=F8dD3CV%2FIQz04Jxif1I%3D&nk2=AHtvjW8YqT8%2FasY%3D&id2=UUpgQcITx5aSbEtnAw%3D%3D',
    'csg': '335fdf8d',
    'lgc': 'carlos_tony',
    'cancelledSubSites': 'empty',
    'cookie17': 'UUpgQcITx5aSbEtnAw%3D%3D',
    'dnk': 'carlos_tony',
    'skt': 'cd61073b7df773a8',
    'existShop': 'MTcwMjk0OTA3Nw%3D%3D',
    'uc4': 'nk4=0%40AhVnII8Q4ZrE1VjidMAeVx16B2XR6w%3D%3D&id4=0%40U2gqztuTAcUe9MtIt5kC0f%2B6e%2FjXiSF0',
    'tracknick': 'carlos_tony',
    '_cc_': 'UIHiLt3xSw%3D%3D',
    '_l_g_': 'Ug%3D%3D',
    'sg': 'y5e',
    '_nk_': 'carlos_tony',
    'cookie1': 'BxNTQvUxpGvSruYWU9Lw1TZ%2F6MO3zr7Im18x7k%2FC%2Bwo%3D',
    'mt': 'ci=0_1',
    'uc1': 'pas=0&cookie14=UoYelzVPun%2B%2FTg%3D%3D&existShop=false&cookie15=URm48syIIVrSKA%3D%3D&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie21=WqG3DMC9Eman',
    'x5sec': '7b22726174656d616e616765723b32223a223862333039333534653461313534633138626331366563373064323432303637434e7a7067367747454e485a695a3046476738794d6a45334d446b324e6a4d314e5463314f7a4d776d63613651513d3d222c22733b32223a2236626237303238353561306331396261227d',
    'tfstk': 'ewWwUjxpfReZMYi5_Bv2UP6K4599CLU7utTXmijDfFYG1EMV3eSuXFNY6Z5Fowd6S1Tj3t8FSxO13iH2mibYXEZTOGI9HK47PKy5XGei60UQFwGosl90PzwIODAT5Kf_lvMlxoA_9JcvZmsv-9xYCzpYrZYEnYoJbCAQeeDmn9-NYUjgMxDcLhRN4P3vxx_AH1umgCxpYUZUYUl2iGQPeIHnMjdT_H87jwGxMCxpYUZUYjhv6O-ePlbC.',
    'l': 'fBjt-SJeP1cgb9UfBOfZnurza77TpIRfguPzaNbMi9fPObfJ5KM5W1CYr4TvCnGVEsmwR3S3hc2kBXY3uyUBhEGfIqlBs2JZFdLnwpzHU',
    'isg': 'BOXl2eKk7GSkPghNIRTXezOG9KEfIpm0MSh1TOfKm5wv_gRwr3PZhOeYiGKIfrFs',
}

headers = {
    'authority': 'rate.taobao.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': '_samesite_flag_=true; cookie2=17b7a71bdd2fdaf129ba6f5be4886894; t=6bc3a374ef61e40a3ef3eb14df43eabb; _tb_token_=ee5196f01e777; thw=cn; _m_h5_tk=d81f72cb37588a9acad44a1b43328ebe_1702954754360; _m_h5_tk_enc=6859e95c3da50863a38af2dc676f7751; sgcookie=E100EL2KKzTKwN71OEM772d3ZoebzxD%2FIHv7nuEAJQAzdiCuvQRIGxY6tIjteDZIKjjxoSBuA%2B0sS5CqXvOxyDXK2FxJpZ2SF2vQKRtEryq30wI%3D; unb=2217096635575; uc3=lg2=V32FPkk%2Fw0dUvg%3D%3D&vt3=F8dD3CV%2FIQz04Jxif1I%3D&nk2=AHtvjW8YqT8%2FasY%3D&id2=UUpgQcITx5aSbEtnAw%3D%3D; csg=335fdf8d; lgc=carlos_tony; cancelledSubSites=empty; cookie17=UUpgQcITx5aSbEtnAw%3D%3D; dnk=carlos_tony; skt=cd61073b7df773a8; existShop=MTcwMjk0OTA3Nw%3D%3D; uc4=nk4=0%40AhVnII8Q4ZrE1VjidMAeVx16B2XR6w%3D%3D&id4=0%40U2gqztuTAcUe9MtIt5kC0f%2B6e%2FjXiSF0; tracknick=carlos_tony; _cc_=UIHiLt3xSw%3D%3D; _l_g_=Ug%3D%3D; sg=y5e; _nk_=carlos_tony; cookie1=BxNTQvUxpGvSruYWU9Lw1TZ%2F6MO3zr7Im18x7k%2FC%2Bwo%3D; mt=ci=0_1; uc1=pas=0&cookie14=UoYelzVPun%2B%2FTg%3D%3D&existShop=false&cookie15=URm48syIIVrSKA%3D%3D&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie21=WqG3DMC9Eman; x5sec=7b22726174656d616e616765723b32223a223862333039333534653461313534633138626331366563373064323432303637434e7a7067367747454e485a695a3046476738794d6a45334d446b324e6a4d314e5463314f7a4d776d63613651513d3d222c22733b32223a2236626237303238353561306331396261227d; tfstk=ewWwUjxpfReZMYi5_Bv2UP6K4599CLU7utTXmijDfFYG1EMV3eSuXFNY6Z5Fowd6S1Tj3t8FSxO13iH2mibYXEZTOGI9HK47PKy5XGei60UQFwGosl90PzwIODAT5Kf_lvMlxoA_9JcvZmsv-9xYCzpYrZYEnYoJbCAQeeDmn9-NYUjgMxDcLhRN4P3vxx_AH1umgCxpYUZUYUl2iGQPeIHnMjdT_H87jwGxMCxpYUZUYjhv6O-ePlbC.; l=fBjt-SJeP1cgb9UfBOfZnurza77TpIRfguPzaNbMi9fPObfJ5KM5W1CYr4TvCnGVEsmwR3S3hc2kBXY3uyUBhEGfIqlBs2JZFdLnwpzHU; isg=BOXl2eKk7GSkPghNIRTXezOG9KEfIpm0MSh1TOfKm5wv_gRwr3PZhOeYiGKIfrFs',
    'referer': 'https://item.taobao.com/item.htm?id=706694913228&ns=1&abbucket=9#detail',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

params = {
    'auctionNumId': '706694913228',
    'userNumId': '753804486',
    'currentPageNum': '1',
    'pageSize': '20',
    'rateType': '',
    'orderType': 'sort_weight',
    'attribute': '',
    'sku': '',
    'hasSku': 'false',
    'folded': '0',
    'ua': '098#E1hv7pvEvb6vUvCkvvvvvjinP2qyljr2R2spzj3mPmPZljYWR25ZAjtjnLFO6jEb3QhvCvvhvvvtvpvhvvvvvvhCvvOvCvvvphvEvpCWHvAkvvwS3wealf4AbDdn+beGeFtQ7JAEAX7Qrc+O3w0x9EyaOpNxKOzBrbwKC+eQ64oYKLaJ6O03I2uZRlkHsX7vVC6AxYjxAfyp+uyCvv9vvUCVPMkkXIyCvvwUvUVvwZPvKphv8vvvvvCvpvvvvvmvx6CvmPwvvUEdphvWe9vv9ervpvsXvvmm46Cv2nyPvpvhvv2MMTwCvvpvvUmm',
    '_ksTS': '1702950840847_1542',
    'callback': 'jsonp_tbcrate_reviews_list',
}

response = requests.get('https://rate.taobao.com/feedRateList.htm', params=params, cookies=cookies, headers=headers)
# print(response.text)
json_match = re.search(r'\((.*)\)', response.text)
if json_match:
    json_data = json_match.group(1)
    # 将提取到的 JSON 数据转换为 Python 对象
    json_data = json.loads(json_data)
# json_data = response.json()
    print(json_data)
    for com in json_data['comments']:
        content = com['content']
        href = 'https://item.taobao.com/item.htm?id=706407719891&ns=1&abbucket=9'
        validname = valid_filename(href)
        with open(f'comment/{validname}.txt', 'a', encoding='utf-8') as file:
            file.write(f'{content}\n')
else:
    print("No JSON data found in the response.")