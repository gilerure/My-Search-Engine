import cv2, os, re
import numpy as np
import urllib.request
import threading

def url_to_img(img_url):
    try:
        resp = urllib.request.urlopen(img_url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    except:
        return np.array([])
    
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
            content = content.lstrip("Product URL").rstrip('\n')
            product["prd_url"] = content
            continue
        if(re.match("Price:", content)):
            content = content.lstrip("Price").rstrip('\n')
            product["price"] = content
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

# 使用方法
print(picture_detection("search/input.jpg", "search/newData"))
