import os
import time
import pandas as pd
from scholarly import scholarly
from datetime import datetime
import list_parser
import logging
import re


logging.basicConfig(filename='scholar_list.log', level=logging.DEBUG)

def _crawl(keyword,max_num):
    '''
    scholarly api 를 사용하여 데이터 수집,
    차단 심함, 중간부터 재수집 불가능, 처음부터 수집만 가능함
    api로 가져올수 있는 data는 최대한 수집하고 naver_list와 포맷 맞춤
    수집된 데이터를 csv로 저장
    :param keyword:
    :return:
    '''
    search_query = scholarly.search_pubs(keyword)
    if max_num < 1000:
        total = max_num
    else:
        total = 1000
    for i in range(total):
        try:
            time.sleep(3)
            data = next(search_query)
            rank = data.bib.get('gsrank')
            search_page = int(((int(rank) + 9)/10)*10)
            page = {
                'rank': rank,
                'search_url': f'https://scholar.google.co.kr/scholar?start={search_page}&q={keyword}&hl=ko&as_sdt=0,5',
                'search_keyword': keyword,
                'author': str(data.bib.get('author')).replace('[','').replace(']',''),
                'affiliation': '', #소속
                'doi': '',
                'keyword' : '',
                'doi_url': data.bib.get('url'),
            }
            logging.info(page)
            _csv_save(page)
            _txt_save(page)

        except Exception as e:
            logging.info(f'search Keyword : {keyword}')
            logging.error(f'Error : {e}')
            break

    list_parser._pdf_parser('scholar', keyword)


def _csv_save(data):
    '''
    api를 사용한 data를 csv로 저장하는 함수
    :param data:
    :return:
    '''
    now = datetime.now()
    now = str(now)[:10].replace('-', '')

    result = []
    result.append(data)
    dataframe = pd.DataFrame(result)
    keyword = data.get('search_keyword')
    text = re.compile('[^ㄱ-ㅣ가-힣a-zA-Z0-9]+')
    file_name = text.sub('', keyword)

    if not os.path.exists(f'scholar_{now}_{file_name}.csv'):
        dataframe.to_csv(f"scholar_{now}_{file_name}.csv", mode='a', encoding='utf-8-sig', sep=",",
                         index=False)
    else:
        dataframe.to_csv(f"scholar_{now}_{file_name}.csv", mode='a', encoding='utf-8-sig', sep=",",
                         header=False, index=False)




def _txt_save(data):
    '''
    txt 파일 생성
    :param data:
    {'rank': 1, 'search_url': 'https://academic.naver.com/article.naver?doc_id=429211580',
    'search_keyword': 'hcho',
    'author': 'Kwon Dong Wook, Seo Phil Won, Kim Geo Jong, Hong Sung Chang',
    'affiliation': 'Department of Environmental Energy Engineering, Graduate School of Kyonggi University, 94-6 San, Iui-dong, Youngtong-ku, Suwon-si, Gyeonggi-do 443-760, Republic of KoreaDepartment of Research & Development, Ceracomb Co., Ltd., 312-26, Deuksan-dong, Asansi, Chungnam 336-120, Republic of Korea', 'doi': 'http://dx.doi.org/10.1016/j.apcatb.2014.08.024', 'keyword': 'HCHO, Room temperature, Humidity, Pt/TiO2, Oxidation', 'doi_url': 'https://linkinghub.elsevier.com/retrieve/pii/S0926337314005025'}
    :return:
    '''
    now = datetime.now()
    now = str(now)[:10].replace('-', '')
    result = []
    result.append(data)
    dataframe = pd.DataFrame(result)
    keyword = data.get('search_keyword')
    text = re.compile('[^ㄱ-ㅣ가-힣a-zA-Z0-9]+')
    file_name = text.sub('', keyword)

    if not os.path.exists(f'scholar_{now}_{file_name}.txt'):
        dataframe.to_csv(f"scholar_{now}_{file_name}.txt", index=False, sep=",")
    else:
        dataframe.to_csv(f'scholar_{now}_{file_name}.txt', mode='a+', index=False, header=None, sep=",")




if __name__ == '__main__':
    s_time = datetime.now()
    _crawl('dense',200)
    print(datetime.now() - s_time)
