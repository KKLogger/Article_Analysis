from toWeb import makeImage
from toWeb import m_preprocessing
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
# df = pd.read_csv('C:/Projects/articleAnalysis/result/naver_20201202_hchoremoval.csv',encoding='utf-8-sig')
df = pd.read_csv(
    "C:/Users/koc08/PycharmProjects/article_analysis/toWeb/result/article_list.csv",
    encoding="utf-8-sig",
)
dict_data = df.to_dict("records")
all_tokens = list()
all_sentences = list()
s_time = datetime.now()
dirname = "result"
PATH = os.getcwd() + f"/{dirname}/"
# idx = 8
# dict_data = dict_data[idx:idx+1]
for dict in dict_data:
    abstract = dict["abstract"]
    if type(abstract) is float:
        abstract = " "
    # highlights = dict['highlight']
    highlights = dict["higtlight"]
    if type(highlights) is float:
        highlights = " "
    lang = dict["lang"]
    if type(lang) is float:
        lang = " "
    if lang == "kor":
        continue
    string = abstract + highlights
    # Token 저장
    tokens = m_preprocessing.get_tokens(string, lang)
    dict["tokens"] = tokens
    # Sentence 저장
    sentences = m_preprocessing.get_sentences(string)
    dict["sentences"] = sentences
    all_tokens = all_tokens + tokens
    all_sentences = all_sentences + sentences

makeImage.get_wordcloud(all_tokens)
print("token is ready..")
# top_token = m_preprocessing.get_top_token(all_tokens)
top_token = []
print("top token is ready..")
try :
    makeImage.get_NG(all_sentences,'eng',top_token)
except :
    error_img = plt.imread('C:/Users/koc08/PycharmProjects/article_analysis/toWeb/result/오류사진.png')
    plt.savefig(PATH + "networkgraph.png", bbox_inches="tight")

print(datetime.now() - s_time)