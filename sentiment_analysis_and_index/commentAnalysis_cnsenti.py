# -*- coding: gb2312 -*-
from cnsenti import Sentiment
import os

senti = Sentiment()

# senti = Sentiment(pos='正面词自定义.txt',  #正面词典txt文件相对路径
#                   neg='负面词自定义.txt',  #负面词典txt文件相对路径
#                   encoding='utf-8')      #两txt均为utf-8编码

comment_path = "D:/University_Courses/电类工程导论C/container/samples4/Group_Task/database/comment/result"
result_path = "D:/University_Courses/电类工程导论C/container/samples4/Group_Task/database/comment/emo_analysis"
conclusion_path = "D:/University_Courses/电类工程导论C/container/samples4/Group_Task/database/comment/emo_conclusion"

def analysis(comment_path, result_path):
    # args: comment_path: the path of the comment files
    #       result_path: the path of the analysis result files
    # process all the files in the comment_path, and write the emo-analysis result to the result_path

    for root, dirs, files in os.walk(comment_path):
        for file in files:
            print("processing file: ", file)
            com_path = os.path.join(root, file)
            res_path = os.path.join(result_path, file)
            com_file_lines = open(com_path, 'r', encoding='utf-8').readlines()
            res_file = open(res_path, 'w', encoding='utf-8')
            # open the comment file and the result file

            for c in com_file_lines:
                print(">>> " + c)
                emot = senti.sentiment_calculate(c)
                if emot['pos'] > emot['neg']: # positive
                    emot = 1
                elif emot['pos'] < emot['neg']: # negative
                    emot = -1
                else: # neutral
                    emot = 0
                res_file.write(str(emot) + '\n')
                print(emot, " written to file")
                # write the analysis result to the result file in the form of 1, -1, 0

def conclude(analysis_path, result_path):
    # args: analysis_path: the path of the analysis result files
    #       result_path: the path of the conclusion files
    # process all the files in the analysis_path, and write the conclusion to the result_path

    for root, dirs, files in os.walk(analysis_path):
        for file in files:
            print("processing file: ", file)
            com_path = os.path.join(root, file)
            com_file_lines = open(com_path, 'r', encoding='utf-8').readlines()
            # open the analysis result file

            pos = 0
            neg = 0
            neu = 0
            for c in com_file_lines:
                if c == '1\n':
                    pos += 1
                elif c == '-1\n':
                    neg += 1
                else:
                    neu += 1
            print("pos: ", pos, "neg: ", neg, "neu: ", neu)
            # count the number of positive, negative and neutral comments

            res_path = os.path.join(result_path, file)
            res_file = open(res_path, 'w', encoding='utf-8')
            res_file.write("pos: " + str(pos) + '\n')
            res_file.write("neg: " + str(neg) + '\n')
            res_file.write("neu: " + str(neu) + '\n')
            total = pos + neg + neu
            # write the number of positive, negative and neutral comments to the conclusion file

            if total != 0:
                pos_rate = float(pos) / (pos + neg + neu)
                neg_rate = float(neg) / (pos + neg + neu)
            else:
                pos_rate = 0
                neg_rate = 0
            res_file.write("pos_rate: " + str(pos_rate) + '\n')
            res_file.write("neg_rate: " + str(neg_rate) + '\n')
            # write the rate of positive and negative comments to the conclusion file

            res_file.close()
      

conclude(result_path, conclusion_path)
