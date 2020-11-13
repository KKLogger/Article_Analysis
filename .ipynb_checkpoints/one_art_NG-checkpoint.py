import nltk
import seaborn as sns
import matplotlib.pyplot as plt
import scikitplot as skplt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn import metrics
import sklearn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.collocations import *
from nltk.tag import pos_tag
from wordcloud import WordCloud
from datetime import datetime
from pandas import DataFrame
import numpy as np
from tqdm import *
import pickle
import os
from nltk.tokenize import word_tokenize
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


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
    '•', '').replace('\xa0', '').replace('Highlights', '')
abstract = soup.find('div', {'id': 'abs0015'}).text.replace('\xa0', '')
keywords = soup.find_all('div', {'class': 'keyword'})
keywords = [x.text.replace('\xa0', '') for x in keywords]
keywords = " ".join(keywords)


sentence = highlights + abstract
sentences = sentence.split('.')
sentences = [x.strip() for x in sentences]
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


df['tokens_rmstop'] = df.tokens.apply(stop_lambda)

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
print(df)
# http://blog.daum.net/geoscience/1408
