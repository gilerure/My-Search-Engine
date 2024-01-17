# SJTU EE208
# This file is used for index creation, and will not be included on web.

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time, math, re, jieba
from datetime import datetime

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.pylucene.search.similarities import PythonSimilarity, PythonClassicSimilarity


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class SimpleSimilarity(PythonClassicSimilarity):

    def lengthNorm(self, numTerms): #长度归一化 default:1/sqrt(length)
        return 1/numTerms

    def tf(self, freq): #单词频率 default:sqrt(freq)
        return freq

    def sloppyFreq(self, distance): #本次匹配中词频率的增量 default:1/(distance + 1)
        return 1/(distance + 1)

    def idf(self, docFreq, numDocs): #逆文档频率 default:(log(numDocs/(docFreq + 1)）+ 1)
        return math.log(1 + (numDocs - docFreq + 0.5)/(docFreq + 0.5))

    def idfExplain(self, collectionStats, termStats): #返回解释对象
        return Explanation.match(1.0, "inexplicable", [])

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = StandardAnalyzer()
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

        # set a new similarity computing method
        config.setSimilarity(SimpleSimilarity())

        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def getTxtAttribute(self, contents, attr):
        m = re.search(attr + ': (.*?)\n',contents)
        if m:
            return m.group(1)
        else:
            return ''


    def indexDocs(self, root, writer):
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if not filename.endswith('.txt'):
                    continue
                print("adding", filename)
                path = os.path.join(root, filename)
                file = open(path, encoding='utf-8', errors='ignore')
                contents = file.read()
                file.close()
                doc = Document()
                doc.add(StringField("name", filename, Field.Store.YES))
                doc.add(StringField("path", path, Field.Store.YES))
                if len(contents) > 0:
                    # imgurl = self.getTxtAttribute(contents, 'imgurl')
                    # doc.add(TextField('imgurl', imgurl, Field.Store.YES))
                    # title = self.getTxtAttribute(contents, 'title')
                    # doc.add(TextField('title', title, Field.Store.YES))
                    # url = self.getTxtAttribute(contents, 'url')
                    # doc.add(TextField('url', url, Field.Store.YES))
                    title = self.getTxtAttribute(contents, 'Title')
                    title = jieba.cut(title)
                    title = " ".join(title) # put space between segmented words
                    doc.add(TextField('title', title, Field.Store.YES))
                    # title of the product
                    brand = self.getTxtAttribute(contents, 'Brand')
                    brand = jieba.cut(brand)
                    brand = " ".join(brand) # put space between segmented words
                    doc.add(TextField('brand', brand, Field.Store.YES))
                    # brand of the product
                    img_url = self.getTxtAttribute(contents, 'Image URL')
                    doc.add(TextField('img_url', img_url, Field.Store.YES))
                    # image url of the product
                    price = self.getTxtAttribute(contents, 'Price')
                    doc.add(TextField('price', price, Field.Store.YES))
                    # price of the product
                    prd_url = self.getTxtAttribute(contents, 'Product URL')
                    doc.add(TextField('prd_url', prd_url, Field.Store.YES))
                    # product url of the product
                    pos = self.getTxtAttribute(contents, 'pos')
                    doc.add(TextField('pos', pos, Field.Store.YES))
                    # number of positive comments
                    neg = self.getTxtAttribute(contents, 'neg')
                    doc.add(TextField('neg', neg, Field.Store.YES))
                    # number of negative comments
                    neu = self.getTxtAttribute(contents, 'neu')
                    doc.add(TextField('neu', neu, Field.Store.YES))
                    # number of neutral comments
                    pos_rate = self.getTxtAttribute(contents, 'pos_rate')
                    doc.add(TextField('pos_rate', pos_rate, Field.Store.YES))
                    # positive rate of the product
                    neg_rate = self.getTxtAttribute(contents, 'neg_rate')
                    doc.add(TextField('neg_rate', neg_rate, Field.Store.YES))
                    # negative rate of the product
                    # tag = self.getTxtAttribute(contents, 'data-tag')
                    # doc.add(TextField('url', tag, Field.Store.YES))
                    # rarity = self.getTxtAttribute(contents, 'data-rarity')
                    # doc.add(TextField('rarity', rarity, Field.Store.YES))
                    # sp = self.getTxtAttribute(contents, 'data-subprofession')
                    # doc.add(TextField('subpro', sp, Field.Store.YES))
                    # doc.add(TextField('contents', contents, Field.Store.YES))
                else:
                    print("warning: no content in %s" % filename)
                writer.addDocument(doc)

if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('Group_Task/database/result/data', 'Group_Task/database/result/index')
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e
