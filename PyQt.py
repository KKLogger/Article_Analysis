import networkx as nx
import plotly.graph_objects as go
import plotly.offline as py
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import lxml
from bs4 import BeautifulSoup as bs
import requests
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import os
import pandas as pd
from tensorflow.keras.preprocessing.text import text_to_word_sequence
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from apyori import apriori
import numpy as np
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
        sentences = get_sentences(highlights, abstract)

        search_keyword = 'mno2'
        # get_NG(tokens)
        # rank = get_association(search_keyword, tokens)
        get_wordcloud(tokens)
        print(self.keywordInput.text())
        wordcloud = QPixmap(PATH+'wordcloud.png')
        wordcloud = wordcloud.scaledToHeight(391)  # 사이즈가 조정
        get_NG(sentences)
        netgraph = QPixmap(PATH + 'networkgraph.png')
        netgraph = netgraph.scaledToHeight(451)  # 사이즈가 조정
        self.label.setPixmap(wordcloud)
        self.label_2.setPixmap(netgraph)


def get_sentences(highlights, abstract):

    sentence = highlights + abstract
    sentences = sentence.split('.')
    sentences = [x.strip() for x in sentences]
    return sentences


def get_association(keyword, tokens):
    import collections
    count_tokens = collections.Counter(tokens)
    keyword = keyword.lower()
    return count_tokens[keyword]


def get_tokens(highlights, abstract, keywords):
    # 다른 토크나이징 함수
    # word_tokenize(highlights)
    # TreebankWordTokenizer().tokenize(highlights)
    # WordPunctTokenizer().tokenize(highlights)

    highlights_token = text_to_word_sequence(highlights)
    abstract_token = text_to_word_sequence(abstract)
    keywords_token = text_to_word_sequence(keywords)
    raw_tokens = highlights_token + abstract_token + keywords_token

    tokens = list()

    for token in raw_tokens:
        if token not in stopwords.words('english'):
            if len(token) > 2:
                tokens.append(token)
    return tokens


def get_wordcloud(tokens):
    wordcloud = WordCloud(background_color='white').generate(" ".join(tokens))
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='lanczos')
    plt.axis('off')
    plt.savefig(PATH+'wordcloud.png', bbox_inches='tight')


def get_NG(sentences):

    df = pd.DataFrame(sentences, columns=['content'])
    nan_value = float("NaN")
    # 결측값 제거
    df.replace(" ", nan_value, inplace=True)
    df.dropna(subset=['content'], inplace=True)
    # 소문자로 통일
    # def lower_alpha(x): return re.sub(r"""\w*\d\w*""", ' ', x.lower())
    # df['content'] = df.content.map(lower_alpha)

    # 특수문자 제거
    # def punc_re(x): return re.sub(r"""[\.,—“”’:;#$?%!&()_'`*""˜{|}~-]""", ' ', x)
    # df['content'] = df.content.map(punc_re)

    def num_re(x): return re.sub(r"""[0-9]""", '', x)

    def short_re(tokens):
        result = list()
        for token in tokens:
            if len(token) > 2:
                result.append(token)
        return result

    df['content'] = df.content.map(num_re)

    # 각 문장을 문장별로 토크나이징

    df['tokens'] = df.content.map(word_tokenize)
    df['tokens'] = df.tokens.map(short_re)

    # remove stop words in tokens
    stop_words = stopwords.words('english')
    new_stop_words = ['said', 'say', 'The', 'the', 'mr']
    stop_words.extend(new_stop_words)
    def stop_lambda(x): return [y for y in x if y not in stop_words]

    df['remove_stopword'] = df.tokens.apply(stop_lambda)
    # DF에서 빈 칸인 공백인 데이터 삭제
    df.dropna(inplace=True)

    idx = df[df['remove_stopword'].apply(lambda x: len(x)) == 0].index
    df = df.drop(idx)

    # Perform basic lemmatization 단어를 기본형태로 변환 ex) 복수형->단수형
    # lemmatizer = WordNetLemmatizer()
    # def lemmatizer_lambda(x): return [lemmatizer.lemmatize(y) for y in x]
    # df['token_lemma_simple'] = df.tokens_stop.apply(lemmatizer_lambda)

    # Perform lemmitization considering parts of speech tagging
    #  각 token의 종류 지정
    # def pos_lambda(x): return nltk.pos_tag(x)
    # df['tokens_pos'] = (df.tokens_stop.apply(pos_lambda))
    # df.head()
    # NN: Noun, singular or mass
    # NNS: Noun, plural
    # IN: Preposition or subordinating conjunction
    # JJ: Adjective
    # RB: Adverb

    # http://blog.daum.net/geoscience/1408
    # APory Alg
    result = (list(apriori(df['remove_stopword'])))
    ap_df = pd.DataFrame(result)
    ap_df['length'] = ap_df['items'].apply(lambda x: len(x))
    ap_df = ap_df[(ap_df['length'] == 2) & (ap_df['support'] >= 0.01)
                  ].sort_values(by='support', ascending=False)

    # 그래프 그리기
    G = nx.Graph()
    ar = ap_df['items']
    G.add_edges_from(ar)

    pr = nx.pagerank(G)
    nsize = np.array([v for v in pr.values()])
    nsize = 4000 * ((nsize - min(nsize)) / (max(nsize)-min(nsize)))
    # Graph Layout
    # pos = nx.planar_layout(G)
    pos = nx.fruchterman_reingold_layout(G)
    pos = nx.spectral_layout(G)
    pos = nx.random_layout(G)
    pos = nx.shell_layout(G)
    # pos = nx.bipartite_layout(G)
    pos = nx.circular_layout(G)
    pos = nx.spring_layout(G)
    pos = nx.kamada_kawai_layout(G)
    # pos = nx.rescale_layout(G)

    plt.figure(figsize=(16, 12))
    plt.axis('off')

    nx.draw_networkx(G, font_size=16, pos=pos, node_color=list(
        pr.values()), node_size=nsize, alpha=0.7, edge_color='.5', cmap=plt.cm.YlGn)
    plt.savefig(PATH+'networkgraph.png', bbox_inches='tight')


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
# os.remove(PATH+'wordcloud.png')
