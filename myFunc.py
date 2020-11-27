import collections
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.text import text_to_word_sequence
from nltk.tokenize import sent_tokenize
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Okt
import requests
import pandas as pd


def get_sentences(highlights, abstract):
    sentence = highlights + abstract
    sentences = sent_tokenize(sentence)
    sentences = [x.strip() for x in sentences]
    return sentences


def get_association(keyword, tokens, lang):
    if lang == "eng":
        count_tokens = collections.Counter(tokens)
        keyword = keyword.lower()
    elif lang == "kor":
        count_tokens = collections.Counter(tokens)
    return count_tokens[keyword]


def get_kr_stopwords():
    """
    >>>input : x , 파일경로를 이용해 불용어 파일 읽기
    >>>output : 불용어 모음 리스트
    """
    with open("한국어불용어.txt", encoding="utf-8") as f:
        stopwords = f.read()
    stopwords = stopwords.split(" ")[0]
    stopwords = stopwords.split("\n")
    return stopwords


def get_tokens(string, lang):
    tokens = list()
    if lang == "eng":
        # 다른 토크나이징 함수
        # word_tokenize(highlights)
        # TreebankWordTokenizer().tokenize(highlights)
        # WordPunctTokenizer().tokenize(highlights)
        raw_tokens = text_to_word_sequence(string)
        for token in raw_tokens:
            if token not in stopwords.words("english"):
                if len(token) > 2:
                    tokens.append(token)
    elif lang == "kor":
        kr_stopwords = get_kr_stopwords()
        sequence_tag = Okt()
        # sequence_tag = Hannanum()
        # sequence_tag = Kkma()
        raw_tokens = sequence_tag.nouns(string)
        # raw_tokens = sequence_tag.morphs(string)
        for token in raw_tokens:
            if token not in kr_stopwords:
                tokens.append(token)
    return tokens


def get_list(keywords, crawl_site):
    """
    >>> rank 정렬, token과 sentences 미리 구함
    """
    # read_csv 대신  keywords에 따라 수집하는 함수 필요
    df = pd.read_csv("eng_article_list.csv", encoding="euc-kr")

    result = list(df.to_dict("records"))

    for item in result:
        # NULL 값 -> 공백 처리
        if type(item["higtlight"]) == float:
            item["higtlight"] = " "
        if type(item["abstract"]) == float:
            item["abstract"] = " "
        if type(item["keywords"]) == float:
            item["keywords"] = " "
        item["data"] = (
            item["abstract"] + "," + item["higtlight"] + "," + item["keywords"]
        )
        item["tokens"] = get_tokens(item["data"], item["lang"])
        item["sentences"] = get_sentences(item["higtlight"], item["abstract"])
    df = pd.DataFrame.from_dict(result)
    df = df.sort_values(by="rank", ascending="False")
    result = list(df.to_dict("records"))

    return result
