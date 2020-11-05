import lxml
from bs4 import BeautifulSoup as bs
import requests
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import os
PATH = os.getcwd() + '\\article_analysis\\Projects\\'
# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType(PATH+"test.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언


class WindowClass(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.searchBtn.clicked.connect(self.searchBtnFunction)

    def searchBtnFunction(self):

        highlights, abstract, keywords = get_data()
        tokens = get_tokens(highlights, abstract, keywords)

        search_keyword = 'mno2'
        # get_NG(tokens)
        # rank = get_association(search_keyword, tokens)
        get_wordcloud(tokens)
        print(self.keywordInput.text())
        pixmap = QPixmap(PATH+'wordcloud.jpg')
        pixmap = pixmap.scaledToHeight(240)  # 사이즈가 조정
        self.label.setPixmap(pixmap)
        self.label_2.setPixmap(pixmap)


def get_association(keyword, tokens):
    import collections
    count_tokens = collections.Counter(tokens)
    keyword = keyword.lower()
    return count_tokens[keyword]


def get_tokens(highlights, abstract, keywords):

    from tensorflow.keras.preprocessing.text import text_to_word_sequence
    # 다른 토크나이징 함수
    # word_tokenize(highlights)
    # TreebankWordTokenizer().tokenize(highlights)
    # WordPunctTokenizer().tokenize(highlights)

    highlights_token = text_to_word_sequence(highlights)
    abstract_token = text_to_word_sequence(abstract)
    keywords_token = text_to_word_sequence(keywords)
    raw_tokens = highlights_token + abstract_token + keywords_token

    tokens = list()
    from nltk.corpus import stopwords
    for token in raw_tokens:
        if token not in stopwords.words('english'):
            if len(token) > 2:
                tokens.append(token)
    return tokens


def get_wordcloud(tokens):
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    wordcloud = WordCloud(background_color='white').generate(" ".join(tokens))
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='lanczos')
    plt.axis('off')
    plt.savefig(PATH+'wordcloud.jpg')


def get_NG(tokens):
    import plotly.offline as py
    import plotly.graph_objects as go
    import networkx as nx
    import collections
    count_tokens = collections.Counter(tokens)
    print(count_tokens)


def get_data():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': "1",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    }
    response = requests.get(
        'https://www.sciencedirect.com/science/article/abs/pii/S0926337317301005', headers=headers)
    soup = bs(response.text, 'html.parser')

    highlights = soup.find('div', {'id': 'abs0010'}).text.replace(
        '•', '').replace('\xa0', '')
    abstract = soup.find('div', {'id': 'abs0015'}).text.replace('\xa0', '')
    keywords = soup.find_all('div', {'class': 'keyword'})
    keywords = [x.text.replace('\xa0', '') for x in keywords]
    keywords = " ".join(keywords)
    return highlights, abstract, keywords


# QApplication : 프로그램을 실행시켜주는 클래스
app = QApplication(sys.argv)

# WindowClass의 인스턴스 생성
myWindow = WindowClass()

# 프로그램 화면을 보여주는 코드
myWindow.show()

# 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
app.exec_()
# os.remove(PATH+'wordcloud.jpg')
