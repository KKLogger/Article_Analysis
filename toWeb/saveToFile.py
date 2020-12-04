from toWeb import makeImage
import m_preprocessing
import pandas as pd

# df = pd.read_csv('C:/Projects/articleAnalysis/result/naver_20201202_hchoremoval.csv',encoding='utf-8-sig')
df = pd.read_csv('C:/Projects/articleAnalysis/article_list.csv',encoding='utf-8-sig')
dict_data = df.to_dict('records')
all_tokens = list()
all_sentences = list()
for dict in dict_data:
    abstract  = dict['abstract']
    if type(abstract) is float:
        abstract = " "
    # highlights = dict['highlight']
    highlights = dict['higtlight']
    if type(highlights) is float:
        highlights = " "
    lang = dict['lang']
    if type(lang) is float:
        lang = " "
    string = abstract + highlights
    #Token 저장
    tokens = m_preprocessing.get_tokens(string,lang)
    dict['tokens'] = tokens
    #Sentence 저장
    sentences = m_preprocessing.get_sentences(string)
    dict['sentences'] = sentences
    all_tokens = all_tokens + tokens
    all_sentences = all_sentences + sentences


makeImage.get_wordcloud(all_tokens)
top_token = m_preprocessing.get_top_token(all_tokens)
# makeImage.get_NG(all_sentences,'eng',top_token)





