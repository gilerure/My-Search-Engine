# SJTU EE208
# This file includes the functions used for searching according to the index created
# by Indexfiles. 

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, math, jieba

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.pylucene.search.similarities import PythonSimilarity, PythonClassicSimilarity


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

def run(searcher, analyzer):
    # while True:
    print()
    print ("Hit enter with no input to quit.")
    command = input("Query:")
    # command = unicode(command, 'GBK')
    # command = 'The Borthers Grimm' 
    if command == '':
        return

    print()
    print ("Searching for:", command)
    command = jieba.cut(command)
    command = " ".join(command) # put space between segmented words
    query = QueryParser("title", analyzer).parse(command)
    scoreDocs = searcher.search(query, 50).scoreDocs
    print ("%s total matching documents." % len(scoreDocs))

    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        print ('title:', deletespace(doc.get("title")), 'score:', scoreDoc.score)
            # print 'explain:', searcher.explain(query, scoreDoc.doc)
    return doc.get("path"), scoreDoc.score

def deletespace(string):
    string = string.replace(' ', '')
    return string

def StartSearch():
    STORE_DIR = "result/index"
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    jieba.load_userdict("userdict.txt")
    print ('lucene', lucene.VERSION)
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    # set a new similarity computing method
    searcher.setSimilarity(SimpleSimilarity()) # simplesimilarity func
    analyzer = StandardAnalyzer()#Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher


StartSearch()