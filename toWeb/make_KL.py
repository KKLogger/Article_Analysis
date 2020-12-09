import json
import collections
from wordcloud import STOPWORDS
import pandas as pd
from toWeb import m_preprocessing
import os
dirname = "temp"
PATH = os.getcwd() + f"/{dirname}/"
def make_top40(df,search_keyword,crawl_site):

    dict_data = df.to_dict("records")
    all_tokens = list()
    raw_tokens =list()
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
        data['tokens'] = tokens
        raw_tokens = raw_tokens + tokens
    for token in raw_tokens:
        if token not in STOPWORDS:
            all_tokens.append(token)
    count_token = collections.Counter(all_tokens)
    count_token = dict(count_token)
    def f2(x):
        return x[1]
    count_token = sorted(count_token.items(),key=f2,reverse=True)
    keyword_list = count_token[:40]
    result = dict()
    for keyword in keyword_list:
        temp_dict = dict()
        temp_list = list()
        for data in dict_data:
            if keyword[0] in data['tokens']:
                temp_list.append(data)
        result[keyword[0]] = temp_list
    with open(PATH + f'{crawl_site}_{search_keyword}.json','w') as  f:
        json.dump(result,f)