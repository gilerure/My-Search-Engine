import requests
import re
import json
import string

def valid_filename(s, max_length=60):
    # 有效字符集合
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    
    # 只保留有效字符，并截断到指定的最大长度
    s = ''.join(c for c in s if c in valid_chars)[:max_length]
    
    return s
# import reque/sts
# import requests

cookies = {
    'cna': 'bO0VHISz+CoBASQD1ABUidPf',
    'OZ_1U_2061': 'vid=v57afa741dcfa6.0&ctime=1702558343&ltime=1702558342',
    'xlly_s': '1',
    'login': 'true',
    'cancelledSubSites': 'empty',
    '_l_g_': 'Ug%3D%3D',
    'dnk': 'carlos_tony',
    'tracknick': 'carlos_tony',
    'lid': 'carlos_tony',
    'unb': '2217096635575',
    'lgc': 'carlos_tony',
    'cookie1': 'BxNTQvUxpGvSruYWU9Lw1TZ%2F6MO3zr7Im18x7k%2FC%2Bwo%3D',
    'cookie17': 'UUpgQcITx5aSbEtnAw%3D%3D',
    '_nk_': 'carlos_tony',
    'sg': 'y5e',
    'cookie2': '17b7a71bdd2fdaf129ba6f5be4886894',
    't': '6bc3a374ef61e40a3ef3eb14df43eabb',
    '_tb_token_': 'ee5196f01e777',
    '_m_h5_tk': '952246b77795344600311e57ba3a5b19_1702958969498',
    '_m_h5_tk_enc': '89419069739fd149f8f3378a96173b05',
    'uc1': 'cookie14=UoYelzVPunhyXw%3D%3D&cookie21=U%2BGCWk%2F7oPIg&existShop=false&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&cookie15=WqG3DMC9VAQiUQ%3D%3D&pas=0',
    'uc3': 'lg2=V32FPkk%2Fw0dUvg%3D%3D&vt3=F8dD3CV%2FIQz04Jxif1I%3D&nk2=AHtvjW8YqT8%2FasY%3D&id2=UUpgQcITx5aSbEtnAw%3D%3D',
    'uc4': 'nk4=0%40AhVnII8Q4ZrE1VjidMAeVx16B2XR6w%3D%3D&id4=0%40U2gqztuTAcUe9MtIt5kC0f%2B6e%2FjXiSF0',
    'sgcookie': 'E100EL2KKzTKwN71OEM772d3ZoebzxD%2FIHv7nuEAJQAzdiCuvQRIGxY6tIjteDZIKjjxoSBuA%2B0sS5CqXvOxyDXK2FxJpZ2SF2vQKRtEryq30wI%3D',
    'csg': '335fdf8d',
    'tfstk': 'eun6f8tAH1fsmo_GOC9ENhu5-oZjCfty5twxExINHlEThiMoGArqHSobcXcLkcrZQXtjEbaakmPqcOmINiSwsFDAcorvaQ-y4ADamodPvNJBfADZhQ1p43kiBOy9UvKyIx4TBMf9oK-O0vXGjGSj4LcqQH_lrDwpi7H_jJ2EARaTwyFCDvoQCPN-Bgl547i4qZ6QriwQap9CoZjNc8Gq5_O7uPe3LnpBday_WJ2Qap9CoZ4TKJuvdp_zC',
    'l': 'fBac_YXcPw9IMs8fBOfwnurza77tdIRfguPzaNbMi9fPOI1J5aqdW1CYla8vCnGVEsF6R3S3hc2kB8YLPy4ehYtOY36n9MptndTnwpzHU',
    'isg': 'BIqKaEks20XBVFceTV8z7bYs23Asew7V0gGKPRTDEF1qxyuB_Av25MMx1zMbN4Zt',
}

headers = {
    'authority': 'h5api.m.tmall.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'cna=bO0VHISz+CoBASQD1ABUidPf; OZ_1U_2061=vid=v57afa741dcfa6.0&ctime=1702558343&ltime=1702558342; xlly_s=1; login=true; cancelledSubSites=empty; _l_g_=Ug%3D%3D; dnk=carlos_tony; tracknick=carlos_tony; lid=carlos_tony; unb=2217096635575; lgc=carlos_tony; cookie1=BxNTQvUxpGvSruYWU9Lw1TZ%2F6MO3zr7Im18x7k%2FC%2Bwo%3D; cookie17=UUpgQcITx5aSbEtnAw%3D%3D; _nk_=carlos_tony; sg=y5e; cookie2=17b7a71bdd2fdaf129ba6f5be4886894; t=6bc3a374ef61e40a3ef3eb14df43eabb; _tb_token_=ee5196f01e777; _m_h5_tk=952246b77795344600311e57ba3a5b19_1702958969498; _m_h5_tk_enc=89419069739fd149f8f3378a96173b05; uc1=cookie14=UoYelzVPunhyXw%3D%3D&cookie21=U%2BGCWk%2F7oPIg&existShop=false&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&cookie15=WqG3DMC9VAQiUQ%3D%3D&pas=0; uc3=lg2=V32FPkk%2Fw0dUvg%3D%3D&vt3=F8dD3CV%2FIQz04Jxif1I%3D&nk2=AHtvjW8YqT8%2FasY%3D&id2=UUpgQcITx5aSbEtnAw%3D%3D; uc4=nk4=0%40AhVnII8Q4ZrE1VjidMAeVx16B2XR6w%3D%3D&id4=0%40U2gqztuTAcUe9MtIt5kC0f%2B6e%2FjXiSF0; sgcookie=E100EL2KKzTKwN71OEM772d3ZoebzxD%2FIHv7nuEAJQAzdiCuvQRIGxY6tIjteDZIKjjxoSBuA%2B0sS5CqXvOxyDXK2FxJpZ2SF2vQKRtEryq30wI%3D; csg=335fdf8d; tfstk=eun6f8tAH1fsmo_GOC9ENhu5-oZjCfty5twxExINHlEThiMoGArqHSobcXcLkcrZQXtjEbaakmPqcOmINiSwsFDAcorvaQ-y4ADamodPvNJBfADZhQ1p43kiBOy9UvKyIx4TBMf9oK-O0vXGjGSj4LcqQH_lrDwpi7H_jJ2EARaTwyFCDvoQCPN-Bgl547i4qZ6QriwQap9CoZjNc8Gq5_O7uPe3LnpBday_WJ2Qap9CoZ4TKJuvdp_zC; l=fBac_YXcPw9IMs8fBOfwnurza77tdIRfguPzaNbMi9fPOI1J5aqdW1CYla8vCnGVEsF6R3S3hc2kB8YLPy4ehYtOY36n9MptndTnwpzHU; isg=BIqKaEks20XBVFceTV8z7bYs23Asew7V0gGKPRTDEF1qxyuB_Av25MMx1zMbN4Zt',
    'referer': 'https://detail.tmall.com/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

params = {
    'jsv': '2.7.0',
    'appKey': '12574478',
    't': '1702949179808',
    'sign': 'c08d31055e65dccd224cfea42b9f0a08',
    'api': 'mtop.alibaba.review.list.for.new.pc.detail',
    'v': '1.0',
    'isSec': '0',
    'ecode': '0',
    'timeout': '10000',
    'ttid': '2022@taobao_litepc_9.17.0',
    'AntiFlood': 'true',
    'AntiCreep': 'true',
    'preventFallback': 'true',
    'type': 'json',
    'dataType': 'json',
    # 'callback': 'mtopjsonp4',
    'data': '{"itemId":"682526021470","bizCode":"ali.china.tmall","channel":"pc_detail","pageSize":20,"pageNum":1}',
}

response = requests.get('https://h5api.m.tmall.com/h5/mtop.alibaba.review.list.for.new.pc.detail/1.0/', params=params, cookies=cookies, headers=headers)

# response = requests.get('https://rate.taobao.com/feedRateList.htm', params=params, cookies=cookies, headers=headers)
print(response.text)

json_data = response.json()
for com in json_data['data']['module']['reviewVOList']:
    content = com['reviewWordContent']
    href = 'https://detail.tmall.com/item.htm?id=682526021470&ns=1&abbucket=9'
    validname = valid_filename(href)
    with open(f'comment/{validname}.txt', 'a', encoding='utf-8') as file:
        file.write(f'{content}\n')
