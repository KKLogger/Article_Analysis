from nltk.tokenize import sent_tokenize
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Okt
import matplotlib.pyplot as plt
from myFunc import *
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from apyori import apriori
from myFunc import *
import requests
from bs4 import BeautifulSoup as bs
import os
import re
import matplotlib.font_manager as fm

font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
plt.rc("font", family=font_name)
PATH = os.getcwd() + "\\article_analysis\\Projects\\"


def get_data():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    }
    response = requests.get(
        "https://www.sciencedirect.com/science/article/abs/pii/S0926337317301005",
        headers=headers,
    )
    soup = bs(response.text, "html.parser")

    highlights = (
        soup.find("div", {"id": "abs0010"}).text.replace("•", " ").replace("\xa0", "")
    )
    abstract = soup.find("div", {"id": "abs0015"}).text.replace("\xa0", "")
    keywords = soup.find_all("div", {"class": "keyword"})
    keywords = [x.text.replace("\xa0", "") for x in keywords]
    keywords = " ".join(keywords)
    lang = "Eng"

    return highlights, abstract, keywords, lang


def get_NG(sentences, lang):

    df = pd.DataFrame(sentences, columns=["content"])
    nan_value = float("NaN")
    # 결측값 제거
    df.replace(" ", nan_value, inplace=True)
    df.dropna(subset=["content"], inplace=True)
    # 소문자로 통일
    # def lower_alpha(x): return re.sub(r"""\w*\d\w*""", ' ', x.lower())
    # df['content'] = df.content.map(lower_alpha)

    # 특수문자 제거
    # def punc_re(x): return re.sub(r"""[\.,—“”’:;#$?%!&()_'`*""˜{|}~-]""", ' ', x)
    # df['content'] = df.content.map(punc_re)

    def num_re(x):
        return re.sub(r"""[0-9]""", "", x)

    def short_re(tokens):
        result = list()
        for token in tokens:
            if len(token) > 2:
                result.append(token)
        return result

    df["content"] = df.content.map(num_re)

    # 각 문장을 문장별로 토크나이징
    df["tokens"] = [get_tokens(x, lang) for x in df["content"]]
    print(df)
    df["tokens"] = df.tokens.map(short_re)
    print("done")
    # remove stop words in tokens
    if lang == "Eng":
        stop_words = stopwords.words("english")
        new_stop_words = ["said", "say", "The", "the", "mr"]
        stop_words.extend(new_stop_words)

        def stop_lambda(x):
            return [y for y in x if y not in stop_words]

        df["remove_stopword"] = df.tokens.apply(stop_lambda)
    elif lang == "Kor":
        stop_words = get_kr_stopwords()

    # DF에서 빈 칸인 공백인 데이터 삭제
    df.dropna(inplace=True)
    idx = df[df["remove_stopword"].apply(lambda x: len(x)) == 0].index
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

    df.to_csv("sample.csv", encoding="euc-kr")
    result = list(apriori(df["remove_stopword"]))
    print(result)
    ap_df = pd.DataFrame(result)

    ap_df["length"] = ap_df["items"].apply(lambda x: len(x))
    ap_df = ap_df[(ap_df["length"] == 2) & (ap_df["support"] >= 0.01)].sort_values(
        by="support", ascending=False
    )

    # 그래프 그리기
    G = nx.Graph()
    ar = ap_df["items"]
    G.add_edges_from(ar)

    pr = nx.pagerank(G)
    nsize = np.array([v for v in pr.values()])
    nsize = 7000 * ((nsize - min(nsize)) / (max(nsize) - min(nsize)))
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

    plt.figure(figsize=(16, 9), dpi=1000)
    plt.axis("off")

    nx.draw_networkx(
        G,
        font_size=20,
        font_weight="bold",
        pos=pos,
        node_color=list(pr.values()),
        node_size=nsize,
        alpha=0.7,
        cmap=plt.cm.YlGn,
        font_family=font_name,
        width=1,
    )
    plt.savefig(PATH + "networkgraph.png", bbox_inches="tight")


text = open("C:/Users/jlee/Downloads/미래로 가는 길.txt", encoding="euc-kr").read()
text.replace("\n", "")
highlights = text
abstract = text
keywords = "안녕.그래"
lang = "Kor"
# highlights, abstract, keywords, lang = get_data()

sentences = sent_tokenize(highlights + abstract)

get_NG(sentences, lang)
