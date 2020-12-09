from toWeb import makeImage
from toWeb import m_preprocessing
from toWeb import make_KL
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
'''
함수 명 및 .py 파일 수정 !! argv 형태로 인자를 전달해줄 것인가?

'''
dirname = "temp"
PATH = os.getcwd() + f"/{dirname}/"
# df = pd.read_csv('C:/Projects/articleAnalysis/result/naver_20201202_hchoremoval.csv',encoding='utf-8-sig')
crawl_site = 'naver'
search_keyword = 'hcho'
df = pd.read_csv(
    PATH + f'{search_keyword}_{crawl_site}.csv',
    encoding="utf-8-sig",
)
s_time = datetime.now()
# idx = 33

# dict_data = dict_data[idx:idx+1]
make_KL.make_top40(df,search_keyword,crawl_site)
makeImage.make_wordcloud(df,search_keyword,crawl_site)
makeImage.make_networkgraph(df,crawl_site)
print(datetime.now() - s_time)
