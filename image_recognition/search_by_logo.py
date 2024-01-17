#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, os, shutil, re
import numpy as np
import urllib.request
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader

# 对爬取结果按照品牌分类
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
    # classification("search/result/data", "newData")
    # target = "search/logo.jpg"
    # folder_path = "search/newData"
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

# classification("search/data", "search/newData")
print(logo_detection("search/logo3.jpg", "search/newData"))