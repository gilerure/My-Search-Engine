# SJTU EE208
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene,jieba, math
from org.apache.lucene.search.highlight import Highlighter
from java.io import File
from java.nio.file import Path
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleFragmenter, SimpleHTMLFormatter
from org.apache.pylucene.search.similarities import PythonSimilarity, PythonClassicSimilarity
from typing import KeysView
from flask import Flask, redirect, render_template, request, url_for
import urllib.error
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

import cv2, os, shutil, re
import numpy as np
import urllib.request
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader
import threading
from time import sleep

'''
import re
from translate import Translator
from gpt4all import GPT4All
'''

class SimpleSimilarity(PythonClassicSimilarity):

    def lengthNorm(self, numTerms): #长度归一化 default:1/sqrt(length)
        return 1 / numTerms

    def tf(self, freq): #单词频率 default:sqrt(freq)
        return freq

    def sloppyFreq(self, distance): #本次匹配中词频率的增量 default:1/(distance + 1)
        return 1/(distance + 1)

    def idf(self, docFreq, numDocs): #逆文档频率 default:(log(numDocs/(docFreq + 1)）+ 1)
        return math.log(1 + (numDocs - docFreq + 0.5)/(docFreq + 0.5))

    def idfExplain(self, collectionStats, termStats): #返回解释对象
        return Explanation.match(1.0, "inexplicable", [])

def get_comprehensive_score(score, pos, neg, neu, penalty = 3):
    # score: search score
    # pos: positive comment count
    # neg: negative comment count
    # neu: neutral comment count
    # penalty: penalty per negative comment
    # calculate the comprehensive score of a product
    
    if pos + neg + neu == 0:
        return score
    comment_score = float(pos - neg * penalty) / (pos + neg + neu)
    comprehensive_score = score * (1 + comment_score)
    return comprehensive_score

def sort(products: list, sort_method = 3):
    # sort_method: 1. search score
    #              2. pos_rate
    #              3. comprehensive_score
    #              4. price
    # sort the result by the sort method
    # sort by comprehensive_score by default
    
    if sort_method == 1:
        products.sort(key = lambda x: x['search_score'], reverse = True)
    elif sort_method == 2:
        products.sort(key = lambda x: x['pos_rate'], reverse = True)
    elif sort_method == 3:
        products.sort(key = lambda x: x['comprehensive_score'], reverse = True)
    elif sort_method == 4:
        products.sort(key = lambda x: x['price'])
    else:
        print('Error: sort method not found!')
        return
    return products

def run(searcher, analyzer, command, sort_method = 3):
    # sort_method: the way to sort the result. comprehensive_score by default
    
    # while True:
    if command == '':
        return
    
    products = []
    score_threshold = 0 # threshold for score of each token
    
    print()
    print ("Searching for:", command)
    
    command = jieba.cut(command)
    command = list(command)
    cmd_tokens = len(command) # number of tokens in command
    command = " ".join(command) # put space between segmented words
    query = QueryParser("title", analyzer).parse(command)
    scoreDocs = searcher.search(query, 500).scoreDocs # more than 500 may cause massive time consumption
    print ("%s total matching documents." % len(scoreDocs))

    for i, scoreDoc in enumerate(scoreDocs):
        product = {}
        if scoreDoc.score < score_threshold * cmd_tokens:
            continue
        doc = searcher.doc(scoreDoc.doc)
        product['title'] = deletespace(doc.get("title"))
        product['prd_url'] = doc.get("prd_url")
        product['price'] = doc.get("price")
        product['img_url'] = doc.get("img_url")
        product['brand'] = doc.get("brand")
        product['file_path'] = doc.get("path")
        product['search_score'] = scoreDoc.score
        product['pos_rate'] = doc.get("pos_rate")
        product['comprehensive_score'] = get_comprehensive_score(scoreDoc.score, 
                                                       int(doc.get("pos").rstrip('\n')), 
                                                       int(doc.get("neg")), 
                                                       int(doc.get("neu")))
        products.append(product)
    print("Search finished!")
        
    # prd_url = prodcut url
    # img_url = image url
    # there's no sales volume cuz we didn't crawl it

    # there're 4 ways to sort the result
    # 1. sort by search score
    # 2. sort by pos_rate
    # 3. sort by comprehensive_score
    # 4. sort by price
    products = sort(products, sort_method)

    return products # all return in a list, each element is a dict

def deletespace(string):
    string = string.replace(' ', '')
    return string

def filter_by_brand(products, brand_range):
    # products: a list of products
    # multi_hot: a list of brands that the user wants to search
    # filter the products by the brands the user wants to search
    
    if brand_range == []:
        return products
    print(brand_range)
    filtered_products = []
    for product in products:
        for brand in brand_range:
            newBrand = deletespace(product['brand'])
            if brand == newBrand:
                filtered_products.append(product)
                break
    return filtered_products

def filter_by_price(products, price_range):
    # products: a list of products
    # price_range: a list of two numbers, the price range
    # filter the products by the price range
    
    if price_range == []:
        return products
    filtered_products = []
    for product in products:
        if float(product['price']) >= price_range[0] and float(product['price']) <= price_range[1]:
            filtered_products.append(product)
    return filtered_products

app = Flask(__name__)
@app.route('/home', methods=['POST', 'GET'])
def bio_data_form():
    if request.method == "POST":
        keyword = request.form['keyword']
        return redirect(url_for('result', keyword=keyword, method = 3))
    return render_template("Taobao goods Search.html")

@app.route('/about', methods=['POST', 'GET'])
def about():
    if request.method == "POST":
        if 'image' in request.files:
            image = request.files['image']
            return redirect(url_for('result', image = image))
        keyword = request.form['keyword']
        return redirect(url_for('result', keyword=keyword,method = 3))
    return render_template("about.html")

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        if 'question' in request.form:
            question = request.form['question']
            return redirect(url_for('gpt', question = question))
        keyword = request.form['keyword']
        return redirect(url_for('result', keyword=keyword,method = 3))
    return render_template("contact.html")

@app.route('/result', methods=['POST','GET'])
def result():
    t = []
    u = []
    p = []
    img = []
    b = []
    com = []
    pos = []
    name = ['搜索指数','好评率','综合评价指数','价格']
    
    STORE_DIR = "result/index"
    jieba.load_userdict("userdict.txt")
    print ('lucene', lucene.VERSION)
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    vm_env.attachCurrentThread()
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    # set a new similarity computing method
    searcher.setSimilarity(SimpleSimilarity()) # simplesimilarity func
    analyzer = StandardAnalyzer()#Version.LUCENE_CURRENT)
    if 'keyword' in request.args:
        keyword = request.args.get('keyword')
    elif 'keyword' in request.form:
        keyword = request.form.get('keyword')
    else:
        return redirect(url_for('bio_data_form'))
        
    method = int(request.args.get('method',3))
    selected_brands = []
    if 'brands' in request.form:
        selected_brands = request.form.getlist('brands')
        print(selected_brands)
    price = []
    if 'price1' in request.args:
        price1 = int(request.args.get('price1'))
        price2 = int(request.args.get('price2'))
        price.append(price1)
        price.append(price2)
    if keyword == '':
        return redirect(url_for('bio_data_form'))
    keyword = ' '.join(jieba.cut(keyword))

    products = run(searcher, analyzer,keyword,method)
    products = filter_by_price(products,price)
    products = filter_by_brand(products,selected_brands)
    for i in range(len(products)):
        t.append(products[i]['title'])
        u.append(products[i]['prd_url'])
        p.append(products[i]['price'])
        img.append(products[i]['img_url'])
        b.append(products[i]['brand'])
        com.append(round(products[i]['comprehensive_score'],4))
        pos.append(round(float(products[i]['pos_rate']),4))
    page = int(request.args.get('page', 1))  # 当前页，默认为第一页面
    per_page = 50                            # 每页显示的结果数量，可以自己设定
    start = (page - 1) * per_page
    end = start + per_page
    paged_results = t[start:end]             # 取当前页面的结果
    paged_urls = u[start:end]
    paged_prices = p[start:end]

    del searcher
    length = min(len(t),len(u))
    length = min(length,len(p))
    total_results = length
    total_pages = (total_results + per_page - 1) // per_page
    current_t = len(paged_results)

    return render_template("search.html", keyword=keyword, length=current_t, img = img, brand = b,price = price,
                           u=paged_urls, t=paged_results, p=paged_prices, name = name, com = com, pos = pos,
                           page=page, total_pages=total_pages, total_results = total_results, method = method)

def classification(folder_path, storeDir):
    for filename in os.listdir(folder_path):
        if(filename.endswith(".txt")):
            print(filename)
            with open (os.path.join(folder_path, filename), encoding="utf-8", errors="ignore") as f:
                data = f.readlines()        
                for content in data:
                    if(re.match("Brand:", content)):
                        break
                brand = content.lstrip("Brand:")
                brand = brand.strip('\n')
                brand = brand.encode("utf-8").decode("utf-8")#.encode("gbk")
                print(brand)
                
                if(not os.path.exists(os.path.join(storeDir, brand))):
                    os.makedirs(os.path.join(storeDir, brand))
                shutil.copy(os.path.join(folder_path, filename), os.path.join(storeDir, brand))
         
def get_comprehensive_score(score, pos, neg, neu, penalty = 3):
    # score: search score
    # pos: positive comment count
    # neg: negative comment count
    # neu: neutral comment count
    # penalty: penalty per negative comment
    # calculate the comprehensive score of a product
    
    if pos + neg + neu == 0:
        return score
    comment_score = float(pos - neg * penalty) / (pos + neg + neu)
    comprehensive_score = score * (1 + comment_score)
    return comprehensive_score

def getProductInfo(data, filename, score):
    product = dict()
    pos, neg, neu = 0, 0, 0
    for content in data:
        if(re.match("Title:", content)):
            content = content.lstrip("Title:").rstrip('\n')
            product["title"] = content
            continue
        if(re.match("Product URL:", content)):
            content = content.lstrip("Product URL:").rstrip('\n')
            product["prd_url"] = content
            print(content)
            continue
        if(re.match("Price:", content)):
            content = content.lstrip("Price:").rstrip('\n')
            product["price"] = content
            print(content)
            continue
        if(re.match("Image URL:", content)):
            content = content.lstrip("Image URL:").rstrip('\n')
            product["img_url"] = content
            continue
        if(re.match("Brand:", content)):
            content = content.lstrip("Brand:").rstrip('\n')
            product["brand"] = content
            continue
        if(re.match("pos_rate:", content)):
            content = content.lstrip("pos_rate:").rstrip('\n')
            product["pos_rate"] = content
            continue
        if(re.match("pos:", content)):
            pos = float(content.lstrip("pos:").rstrip('\n'))
            continue
        if(re.match("neg:", content)):
            neg = float(content.lstrip("neg:").rstrip('\n'))
            continue
        if(re.match("neu:", content)):
            neu = float(content.lstrip("neu:").rstrip('\n'))
            continue 
    product["search_score"] = score 
    product["file_path"] = filename
    product["comprehensive_score"] = get_comprehensive_score(score,pos, neg, neu)
    return product
         
print('Load model: ResNet50')
#model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model = torchvision.models.resnet50(pretrained=True)
    
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize,
])

class MyCBIR:
    # 图像预处理
    def preprocess(self, img):
        input_image = default_loader(img)
        input_image = trans(input_image)
        input_image = torch.unsqueeze(input_image, 0)
        #print(input_image)
        return input_image

    # 抽取图像特征
    def features(self, x):
        x = model.conv1(x)
        x = model.bn1(x)
        x = model.relu(x)
        x = model.maxpool(x)
        x = model.layer1(x)
        x = model.layer2(x)
        x = model.layer3(x)
        x = model.layer4(x)
        x = model.avgpool(x)
        return x

    # 初始化，得到特征向量
    def __init__(self, img):
        input_image = self.preprocess(img)
        image_feature = self.features(input_image)
        image_feature = image_feature.detach().numpy()
        image_feature = np.ravel(image_feature)
        self.features = image_feature
    
    # 计算相似度
    def compare(self, other):
        v1 = self.features
        v2 = other.features
        normalized_v1 = v1 / np.linalg.norm(v1)
        normalized_v2 = v2 / np.linalg.norm(v2)
        return 1 - np.sqrt(np.sum((normalized_v1-normalized_v2)**2))


# 将用户输入的logo图片和已有的品牌最对比，找到最合适的匹配
def MySIFT(target_img, logo_img):
    # 初始化SIFT检测器
    sift = cv2.SIFT_create()

    # 读取图像
    target = cv2.imread(target_img, cv2.COLOR_BGR2GRAY)
    logo = cv2.imread(logo_img, cv2.COLOR_BGR2GRAY)
    
    # 寻找图像的关键点和描述符
    kp_target, des_target = sift.detectAndCompute(target, None)
    kp_logo, des_logo = sift.detectAndCompute(logo, None)
    
    # 创建FLANN匹配器
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(des_target, des_logo, k=2)

    # 应用比例测试
    good_matches = [m for m,n in matches if m.distance < 0.75*n.distance]
    return len(good_matches)/100


# 整合两种算法完成最佳匹配
def logo_detection(target, folder_path):
    folder_path = "newData"
    match_score = dict()
    target_tool = MyCBIR(target)
    
    # 遍历文件夹中各品牌的logo图片
    for brand in os.listdir(folder_path):
        match_score[brand] = 1
        for filename in os.listdir(os.path.join(folder_path, brand)):
            if (filename.endswith(".jpg") or filename.endswith(".png")):
                path = os.path.join(folder_path, brand, filename)
                print("Processing {}".format(filename))
                
                # 用CBIR算法计算相似度
                logo_tool = MyCBIR(path)
                match_score[brand] *= target_tool.compare(logo_tool)
                # print(match_score)
                
                # 用SIFT算法计算相似度
                match_score[brand] += MySIFT(target, path)/10
                # print(match_score)

    # 对比匹配结果，找到最合适匹配
    match_score = sorted(match_score.items(), key=lambda x : x[1], reverse=True)

    # 返回最佳匹配品牌及其五十个商品信息            
    products = []
    bestBrand = os.path.join(folder_path, match_score[0][0])
    for filename in os.listdir(bestBrand):
        if (filename.endswith(".txt")):
            print("downloading {}".format(filename))
            path = os.path.join(bestBrand, filename)
            product = dict()
            with open (path, encoding="utf-8", errors="ignore") as f:
                data = f.readlines()
                product = getProductInfo(data, filename, match_score[0][1])
                products.append(product)
        if(len(products) >= 50):
            break
    products.sort(key=lambda x:x['comprehensive_score'], reverse=True)
    return products


app.config['UPLOAD_FOLDER'] = 'uploads'  # 设置文件上传的目标文件夹
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #限制文件大小为16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/logo', methods=['POST','GET'])
def upload_logo():
    t = []
    u = []
    p = []
    img = []
    b = []
    com = []
    pos = []
    length = 0
    if request.method == "POST":
        if 'keyword' in request.form:
            keyword = request.form['keyword']
            return redirect(url_for('result', keyword=keyword,method = 3))
        if 'image' not in request.files:
            print(1)
            return redirect(url_for('about'))
        image = request.files['image']
        if image.filename == '':
            return redirect(url_for('about'))
        if image:
            filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], "input.jpg"))
            products = logo_detection("uploads/input.jpg", "newData")
            for i in range(len(products)):
                print(1)
                t.append(products[i]['title'])
                u.append(products[i]['prd_url'])
                p.append(products[i]['price'])
                img.append(products[i]['img_url'])
                b.append(products[i]['brand'])
                com.append(round(products[i]['comprehensive_score'],4))
                pos.append(round(float(products[i]['pos_rate']),4))
                length = len(products)
    
    return render_template("logoSearch.html", length = length, img = img, brand = b, com = com, pos = pos,
                                   u = u, t = t, p = p)

def url_to_img(img_url):
    try:
        resp = urllib.request.urlopen(img_url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    except:
        return np.array([])
    
def process_folder(brand, folder_path, img, sift, flann, des1, products, lock, stop_event):
    for filename in os.listdir(os.path.join(folder_path, brand)):
        if stop_event.is_set():
            break
        if (filename.endswith(".txt")):
            product = dict()
            path = os.path.join(folder_path, brand, filename)
            print("Processing {}".format(filename))
            with open(path, "r") as f:
                data = f.readlines()
                for content in data:
                    if(re.match("Image URL:", content)):
                        content = content.lstrip("Image URL:").rstrip('\n')
                        goods = url_to_img(content)
                        if(goods.any()):
                            kp2, des2 = sift.detectAndCompute(goods, None) 
                            matches = flann.knnMatch(des1, des2, k=2)
                            good_matches = [m for m,n in matches if m.distance < 0.75*n.distance]
                            if(len(good_matches) >= 20):
                                with lock:
                                    product = getProductInfo(data, filename, len(good_matches)/40)
                                    products.append(product)
                                    if len(products) >= 50:
                                        stop_event.set()
                                        return

def picture_detection(input_image, folder_path):
    # 读取图像
    img = cv2.imread(input_image, cv2.IMREAD_COLOR)

    # 初始化SIFT检测器
    sift = cv2.SIFT_create()
    
    # 寻找关键点和描述符
    kp1, des1 = sift.detectAndCompute(img, None)

    # 创建FLANN匹配器
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    
    # 遍历文件夹中各商品图片
    products = []
    lock = threading.Lock()
    stop_event = threading.Event()
    threads = []
    for brand in os.listdir(folder_path):
        thread = threading.Thread(target=process_folder, args=(brand, folder_path, img, sift, flann, des1, products, lock, stop_event))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    products.sort(key=lambda x:x['comprehensive_score'], reverse=True)
    return products


@app.route('/pic', methods=['POST','GET'])
def upload_pic():
    t = []
    u = []
    p = []
    img = []
    b = []
    com = []
    pos = []
    length = 0
    if request.method == "POST":
        if 'keyword' in request.form:
            keyword = request.form['keyword']
            return redirect(url_for('result', keyword=keyword,method = 3))
        if 'image' not in request.files:
            return redirect(url_for('about'))
        image = request.files['image']
        if image.filename == '':
            return redirect(url_for('about'))
        if image:
            filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], "input.jpg"))
            products = picture_detection("uploads/input.jpg", "newData")
            for i in range(len(products)):
                t.append(products[i]['title'])
                u.append(products[i]['prd_url'])
                p.append(products[i]['price'])
                img.append(products[i]['img_url'])
                b.append(products[i]['brand'])
                com.append(round(products[i]['comprehensive_score'],4))
                pos.append(round(float(products[i]['pos_rate']),4))
                length = len(products)

    return render_template("picSearch.html", length = length, img = img, brand = b, com = com, pos = pos,
                                   u = u, t = t, p = p)


CACHE_FILE_PATH = "cache/chat_input.txt"
OUTPUT_FILE_PATH = "cache/chat_output.txt"
ATTRS_FILE_PATH = "cache/chat_attrs.txt"

def read_output():
    file = open(OUTPUT_FILE_PATH, 'r', encoding='utf-8')
    output = file.read()
    file.close()
    return output

def read_attrs():
    file = open(ATTRS_FILE_PATH, 'r', encoding='utf-8')
    attrs = file.readlines()
    for i in range(len(attrs)):
        attrs[i] = attrs[i].replace('\n', '')
    file.close()
    return attrs

def write_input(command):
    file = open(CACHE_FILE_PATH, 'w', encoding='utf-8')
    file.write(command)
    file.close()

@app.route('/gpt', methods=['POST', 'GET'])
def gpt():
    if request.method == "POST":
        keyword = request.form['keyword']
        return redirect(url_for('result', keyword=keyword, method = 3))
    command = request.args.get('question')
    if command == '':
        return redirect(url_for('/contact'))
    write_input(command)
    while read_output() == '':
        print("waiting for output...")
        sleep(1)
        pass
    attrs = read_attrs()
    print(attrs)
    return render_template("gpt.html", command = attrs)


if __name__ == '__main__':
    vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    app.run(debug=True,port = 8080)