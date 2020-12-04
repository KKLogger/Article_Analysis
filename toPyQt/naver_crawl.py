from bs4 import BeautifulSoup
import requests
import json
import re
import time
import pandas as pd
import csv
import os
import random
import logging
from tqdm import tqdm
from datetime import datetime
import list_parser

logging.basicConfig(filename='naver_list.log', level=logging.DEBUG)

def _crawl(keyword,max_num):
    '''
    검색 keyword를 입력하여 해당 keyword를 가지고 list 수집하는 함수
    :param keyword: hcho
    :return: csv and txt file svae
    '''
    page = 1
    url = f'https://academic.naver.com/search.naver?query={keyword}&searchType=1&field=0&docType=1&page={page}'
    soup = _fetch(url)
    total = _total(soup)
    if total > max_num :
        total = max_num
    if total > 2000:
        total = 2000
    logging.info(f'검색어 : {keyword}')
    logging.info(f'논문 수 : {total} // 최대 2000개 까지 수집 가능합니다.')
    url_list = _urlList(keyword, total)
    _parser(url_list, keyword)
    list_parser._pdf_parser('naver', keyword)

def _fetch(url):
    time.sleep(random.uniform(2, 3))
    request_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
    }
    response = requests.get(url, headers=request_header)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def _doifetch(url):
    time.sleep(random.uniform(2, 5))
    request_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
    }
    response = requests.get(url, headers=request_header)
    return response.url


def _total(soup):
    '''
    keyword 검색시 나오는 전체 수 체크하는 부분 최대 2천개 까지 수집 가능하여 2천개 초과시 2천개로 수정
    :return:
    '''
    total = soup.select_one('li.ui_tabnavi_item.on > a > span').get_text().replace(',','')
    return int(total)

def _urlList(keyword, total):
    '''
    keyword 검색시 보여지는 결과물, 최대 2000개 까지 link 수집하는 부분분,

   :param keyword: hcho
    :param total: 2000
    :return: [{'rank': 1,
        'title': 'Characteristics of the HCHO oxidation reaction over Pt/TiO2 '
        'catalysts at room temperature: The effect of relative humidity on '
        'catalytic activity',
        'url': 'https://academic.naver.com/article.naver?doc_id=429211580'} ...]
    '''
    result = []
    start_num = _file_check(keyword)
    if start_num != 1:
        start_page = start_num // 10
    else:
        start_page = 1

    with tqdm() as pbar:
        for page in range(start_page, (total // 10 + 1)):
            url = f'https://academic.naver.com/search.naver?query={keyword}&searchType=1&field=0&docType=1&page={page}'

            soup = _fetch(url)
            board_url = 'https://academic.naver.com'
            rank = (page-1)*10 + 1
            if start_num > rank:
                continue
            for i in soup.select('div.ui_listing > div > ul > li'):

                url = board_url + i.select_one('h4 > a')['href']
                title = i.select_one('h4 > a').get_text().strip()
                page = {
                    'rank': rank,
                    'title': title,
                    'url': url,
                }
                rank += 1
                result.append(page)

            pbar.update()
    return result

def _file_check(keyword) -> int:
    '''
    에러 또는 같은 키워드 재수집시 시간 단축을 위해 같은 날짜 같은 키워드로 검색한 결과물이 있을경우 해당 파일을 읽어 재수집
    :param keyword:
    :return:
    '''
    now = datetime.now()
    now = str(now)[:10].replace('-', '')
    text = re.compile('[^ㄱ-ㅣ가-힣a-zA-Z0-9]+')
    file_name = text.sub('', keyword)
    if not os.path.exists(f'naver_{now}_{file_name}.csv'):
        return 1
    else:
        data = pd.read_csv(f'naver_{now}_{file_name}.csv', encoding='utf-8-sig')
        rank = data['rank'][len(data)-1]
    return rank



def _parser(url_list, search_keyword):
    '''
    keyword 검색시 보여지는 url를 가지고 하나씩 접근하여 논문 pdf를 제공하는 논문 사이트 url 및 기타 데이터 수집
    :param url_list:
    :return:
    '''

    for i in url_list:
        try:
            url = i.get('url')
            rank = i.get('rank')
            soup = _fetch(url)
            key = soup.select('div.ui_listdetail.type2 > dl > dt')
            value = soup.select('div.ui_listdetail.type2 > dl > dd')
            author, affiliation, doi, keyword = '', '', '', ''
            for k, v in zip(key, value):
                if k.get_text() == '저자':
                    author = v.get_text()
                elif k.get_text() == '소속':
                    affiliation = v.get_text()
                elif k.get_text() == 'DOI':
                    doi = v.select_one('a')['href']
                elif k.get_text() == '키워드':
                    keyword = v.get_text()
            if len(doi) < 1:
                doi_url = None
            else:
                try:
                    doi_url = _doifetch(doi)
                except Exception as e:
                    doi_url = ''

                    logging.warning(f'url : {url}')
                    logging.warning(f'error : {e}')

            page = {
                'rank' : rank,
                'search_url': url,
                'search_keyword' : search_keyword,
                'author' : author,
                'affiliation' : affiliation,
                'doi' : doi,
                'keyword' : keyword,
                'doi_url' : doi_url,
            }
            logging.info(page)
            _csv_save(page)
            _txt_save(page)
        except Exception as e:
            logging.warning(f'error : {e}')


def _csv_save(data):
    '''
    수집한 데이터를 csv로 저장하는 함수
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

    if not os.path.exists(f'naver_{now}_{file_name}.csv'):
        dataframe.to_csv(f"naver_{now}_{file_name}.csv", mode='a', encoding='utf-8-sig', sep=",",
                         index=False)

    else:
        dataframe.to_csv(f"naver_{now}_{file_name}.csv", mode='a', encoding='utf-8-sig', sep=",",
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

    if not os.path.exists(f'naver_{now}_{file_name}.txt'):
        dataframe.to_csv(f"naver_{now}_{file_name}.txt", index=False, sep=",")
    else:
        dataframe.to_csv(f'naver_{now}_{file_name}.txt', mode='a+', index=False, header=None, sep=",")





if __name__ == '__main__':

    s_time = datetime.now()
    _crawl('day',200)
    print(datetime.now() - s_time)