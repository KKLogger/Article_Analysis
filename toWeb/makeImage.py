import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from m_preprocessing import *
import os
import re
import matplotlib.font_manager as fm
import time
import sys
import json
import collections
from wordcloud import STOPWORDS
import m_preprocessing

font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
plt.rc("font", family=font_name)
dirname = "temp"
PATH = os.getcwd() + f"/{dirname}/"


def get_wordcloud(tokens, keywords, crawl_site):
    # wordcloud = WordCloud(background_color='white').generate(" ".join(tokens))
    wordcloud = WordCloud(
        font_path="c:/Windows/Fonts/malgun.ttf",
        background_color="white",
        width=1600,
        height=900,
        font_step=10,
        max_words=40,
    ).generate(" ".join(tokens))
    plt.figure(figsize=(16, 9))
    plt.imshow(wordcloud, interpolation="lanczos")
    plt.axis("off")
    plt.savefig(PATH + f"{crawl_site}_{keywords}_wordcloud.png", bbox_inches="tight")
    plt.clf()
    plt.close()


def make_wordcloud(df, keywords, crawl_site):
    dict_data = df.to_dict("records")
    all_tokens = list()
    for data in dict_data:
        abstract = data["abstract"]
        if type(abstract) is float:
            abstract = " "
        highlights = data["highlight"]
        if type(highlights) is float:
            highlights = " "
        lang = data["lang"]
        if type(lang) is float:
            lang = " "
        if lang == "kor":
            continue
        string = abstract + highlights
        # Token 저장
        tokens = m_preprocessing.get_tokens(string, lang)
        all_tokens = all_tokens + tokens
    get_wordcloud(all_tokens, keywords, crawl_site)


def get_NG(sentences, lang, rank, crawl_site):
    if lang == "eng":
        df = pd.DataFrame(sentences, columns=["content"])
        nan_value = float("NaN")
        # 결측값 제거
        df.replace(" ", nan_value, inplace=True)
        df.dropna(subset=["content"], inplace=True)
        # 소문자로 통일
        def lower_alpha(x):
            return re.sub(r"""\w*\d\w*""", " ", x.lower())

        df["content"] = df.content.map(lower_alpha)

        # 특수문자 제거
        def punc_re(x):
            return re.sub(r"""[\.,—“”’:;#$?%!&()_'`*""˜{|}~-]""", " ", x)

        df["content"] = df.content.map(punc_re)

        def num_re(x):
            return re.sub(r"""[0-9]""", "", x)

        def short_re(tokens):
            result = list()

            for token in tokens:
                token = token.replace("‘", "")
                token = token.replace("”", "")
                token = token.replace("“", "")
                token = token.replace("×", "").strip()
                if len(token) > 2:
                    result.append(token)
            return result

        df["content"] = df.content.map(num_re)

        # 각 문장을 문장별로 토크나이징
        df["tokens"] = [get_tokens(x, lang) for x in df["content"]]

        df["tokens"] = df.tokens.map(short_re)

        # remove stop words in tokens
        # if lang == "eng":
        #     stop_words = stopwords.words("english")
        #     new_stop_words = ["said", "say", "The", "the", "mr"]
        #     stop_words.extend(new_stop_words)
        # elif lang == "kor":
        #     stop_words = get_kr_stopwords()

        # def stop_lambda(x):
        #     return [y for y in x if y not in stop_words]

        # df["remove_stopword"] = df.tokens.apply(stop_lambda)
        # DF에서 빈 칸인 공백인 데이터 삭제
        df.dropna(inplace=True)

        # idx = df[df["remove_stopword"].apply(lambda x: len(x)) == 0].index
        # df = df.drop(idx)

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
        # mlxtend Apriori http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/apriori/

        te = TransactionEncoder()
        dataset = list(df["tokens"])

        te_ary = te.fit(dataset).transform(dataset)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        if len(df) > 2:
            ap_df = apriori(df, use_colnames=True, low_memory=True)
            ap_df["length"] = ap_df["itemsets"].apply(lambda x: len(x))
            ap_df = ap_df[
                (ap_df["length"] == 2) & (ap_df["support"] >= 0.01)
            ].sort_values(by="support", ascending=False)
        else:
            # make empty df
            ap_df = pd.DataFrame(columns=["a"])
        if ap_df.empty:
            error_img = plt.imread(PATH + "../graph_error.png")
            plt.imshow(error_img)
            plt.axis("off")
            plt.savefig(
                PATH + f"/network_graph/{crawl_site}_{rank}_networkgraph.png",
                bbox_inches="tight",
            )
            pass
        else:
            # 그래프 그리기
            G = nx.Graph()
            ar = ap_df["itemsets"]
            G.add_edges_from(ar)

            pr = nx.pagerank(G)
            nsize = np.array([v for v in pr.values()])
            if max(nsize) == min(nsize):
                nsize = 7000 * nsize
            else:
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

            plt.figure(figsize=(16, 9), dpi=100)
            plt.axis("off")

            nx.draw_networkx(
                G,
                font_size=20,
                font_weight="bold",
                pos=pos,
                node_color=list(pr.values()),
                node_size=nsize,
                alpha=0.7,
                cmap=plt.cm.GnBu,
                font_family=font_name,
                width=1.5,
            )
            plt.savefig(
                PATH + f"/network_graph/{crawl_site}_{rank}_networkgraph.png",
                bbox_inches="tight",
            )
        plt.clf()
        plt.close()


def make_networkgraph(df, crawl_site):
    dict_data = df.to_dict("records")
    for data in dict_data:
        abstract = data["abstract"]
        if type(abstract) is float:
            abstract = " "
        highlights = data["highlight"]
        if type(highlights) is float:
            highlights = " "
        lang = data["lang"]
        if type(lang) is float:
            lang = " "
        if lang == "kor":
            continue
        string = abstract + highlights
        # Sentence 저장
        sentences = m_preprocessing.get_sentences(string)
        rank = data["rank"]
        get_NG(sentences, lang, rank, crawl_site)


def make_top40(df, search_keyword, crawl_site):

    dict_data = df.to_dict("records")
    all_tokens = list()
    raw_tokens = list()
    for data in dict_data:
        abstract = data["abstract"]
        if type(abstract) is float:
            abstract = " "
        highlights = data["highlight"]
        if type(highlights) is float:
            highlights = " "

        lang = data["lang"]
        if type(lang) is float:
            lang = " "
        if lang == "kor":
            continue
        string = abstract + highlights
        # Token 저장
        tokens = m_preprocessing.get_tokens(string, lang)
        data["tokens"] = tokens
        raw_tokens = raw_tokens + tokens
    for token in raw_tokens:
        if token not in STOPWORDS:
            all_tokens.append(token)
    count_token = collections.Counter(all_tokens)
    count_token = dict(count_token)

    def f2(x):
        return x[1]

    count_token = sorted(count_token.items(), key=f2, reverse=True)
    keyword_list = count_token[:40]
    result = dict()
    for keyword in keyword_list:
        temp_dict = dict()
        temp_list = list()
        for data in dict_data:
            if keyword[0] in data["tokens"]:
                temp_list.append(data)
        result[keyword[0]] = temp_list
    with open(PATH + f"{crawl_site}_{search_keyword}.json", "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    title = sys.argv[1]

    search_keyword = title.split("_")[0]
    crawl_site = title.split("_")[1].split(".")[0]

    df = pd.read_csv(PATH + f"{search_keyword}_{crawl_site}.csv", encoding="utf-8-sig")
    make_wordcloud(df, search_keyword, crawl_site)
    make_top40(df, search_keyword, crawl_site)
    make_networkgraph(df, crawl_site)
