from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import csv
import os
import random
from datetime import datetime
import logging

logging.basicConfig(filename='parser.log', level=logging.DEBUG)

def _doi_crawl(site, page):
    '''
    academic_naver_list 와 scholar-re 에서 수집된 논문 url 과 기타 데이터를 가지고 데이터 수집
    :param site:naver or scholar
    :param page: {'rank': 3, 'search_url': 'https://academic.naver.com/article.naver?doc_id=512219000',
    'search_keyword': 'hcho',
    'author': 'Bingyang Bai, Junhua Li',
    'affiliation': '',
    'doi': 'http://dx.doi.org/10.1021/cs5006663',
    'keyword': '',
    'doi_url': 'https://pubs.acs.org/doi/10.1021/cs5006663'}
    '''
    now = datetime.now()
    now = str(now)[:10].replace('-', '')
    text = re.compile('[^ㄱ-ㅣ가-힣a-zA-Z0-9]+')
    keyword = page.get('search_keyword')
    file_name = text.sub('', keyword)

    rank = page.get('rank')
    search_url = page.get('search_url')
    search_keyword = page.get('search_keyword')
    author = page.get('author')
    affiliation = page.get('affiliation')
    doi = page.get('doi')
    keyword = page.get('keyword')
    doi_url = page.get('doi_url')

    if doi_url is not None:
        time.sleep(random.uniform(1, 3))
        page = {
            'rank': rank,
            'search_url': search_url,
            'search_keyword': search_keyword,
            'author': author,
            'affiliation': affiliation,
            'doi': doi,
            'keyword': keyword,
            'doi_url': doi_url,
        }
        try:
            _url(page, now, file_name, site)
        except Exception as e:
            logging.error(f'error : {e}')

    logging.info('finished doi crawl..')


def _save_parser(site, keyword):
    '''
    중단후 시작할때 이미 저장된 file을 읽어오는것
    :param site : naver or scholar
    :param keyword : hcho
    :return:
    '''
    now = datetime.now()
    now = str(now)[:10].replace('-', '')
    text = re.compile('[^ㄱ-ㅣ가-힣a-zA-Z0-9]+')
    file_name = text.sub('', keyword)
    # data = pd.read_csv(f'{site}_{now}_{file_name}.csv', encoding='utf-8-sig') # csv read
    data = pd.read_csv(f'{site}_{now}_{file_name}.txt', encoding='utf-8-sig') #txt read
    data = data.drop_duplicates(subset=None, keep='first') # 중복제거
    for i in range(len(data)):
        rank = data['rank'][i]
        search_url = data['search_url'][i]
        search_keyword = data['search_keyword'][i]
        author = data['author'][i]
        affiliation = data['affiliation'][i]
        doi = data['doi'][i]
        keyword = data['keyword'][i]
        doi_url = data['doi_url'][i]

        if doi_url is None:
            continue
        logging.info(f'{i} : {len(data)}')
        time.sleep(random.uniform(2, 5))
        page = {
            'rank': rank,
            'search_url': search_url,
            'search_keyword': search_keyword,
            'author': author,
            'affiliation': affiliation,
            'doi': doi,
            'keyword': keyword,
            'doi_url': doi_url,
        }
        try:
            _url(page, now, file_name, site)
        except Exception as e:
            logging.error(f'error : {e}')

        logging.info('(_save_parser) finished parsing data...')


def _url(page, now, file_name, site):
    '''
    논문이 있는 논문 사이트를 가기위한 부분
    논문 사이트가 너무 많아 상위 몇개만 개발함

    각각의 링크들을 타고 수집할수 있는 data 수집후 csv_save
    :param page:
    :param now:
    :param file_name:
    :return:
    '''
    url = page.get('doi_url')
    data = None
    if 'https://iopscience.iop.org/' in url:
        #차단이슈
        pass
    elif 'http://koreascience.or.kr/' in url:
        data = _koreascience(page)
    elif 'https://acp.copernicus.org/' in url:
        data = _acpcopernicus(page)
    elif 'https://amt.copernicus.org/' in url:
        data = _amtcopernicus(page)
    elif 'https://www.mdpi.com/' in url:
        data = _mdpi(page)
    elif 'http://joie.or.kr/' in url:
        data = _joie(page)
    elif 'https://www.nature.com/' in url:
        data = _nature(page)
    elif 'https://linkinghub.elsevier.com/' in url:
        data = _sciencedirect(page)
    elif 'https://www.sciencedirect.com' in url:
        data = _sciencedirectpage(page)
    else:
        pass
    if data is not None:
        _csv_save(data, now, file_name, site)
        _txt_save(data, now, file_name, site)


# def _iopscience(url):
#     # 뒤에 /pdf만 붙이면 있는 것들은 접근가능, but 없어도 접근가능 header 값 체크하기
#     # 차단 이슈 있음, delay 및 방법 찾기
#     pdf_url = url + '/pdf'
#     _pdfSave(pdf_url)


def _fetch(url):
    time.sleep(random.uniform(2, 5))
    request_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
    }
    response = requests.get(url, headers=request_header)
    html = response.text
    response.encoding = 'utf-8'
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def _koreascience(page):
    '''
    :param page:{'rank': 6,
    'search_url': 'https://academic.naver.com/article.naver?doc_id=176993974',
    'search_keyword': '소재개질',
    'author': '박정민, 김희정, 유중환',
    'affiliation': '한국세라믹기술원',
    'doi': 'http://dx.doi.org/10.14478/ace.2015.1104',
    'keyword': 'cool paint, energy efficiency, flake shaped material,...
    'doi_url': 'http://koreascience.or.kr/article/JAKO201607639684447.page'}
    :return:
    '''
    url = page.get('doi_url')
    # uuid = ''
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'

    board_url = 'http://koreascience.or.kr'
    soup = _fetch(url)
    title = soup.select_one('h1.h2').get_text().strip()
    abstract = soup.select_one('p.g-color-gray-dark-v2.text-justify').get_text().strip()
    lang = _lang(abstract)
    keyword = page.get('keyword')
    if lang == 'eng':
        keyword = _korsplit(keyword)
    if 'naver' in page.get('search_url'):
        search_site = 'naver'

    # if soup.select('li > p > a.btn.btn-sm.btn-outline-danger'):
    #     pdf_url = board_url + soup.select_one('li > p > a.btn.btn-sm.btn-outline-danger')['href']
    #     uuid = _pdfSave(pdf_url)
    data = {
        'rank' : page.get('rank'),
        'search_url' : page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title' : title,
        'author' : page.get('author'),
        'doi_url' : page.get('doi'),
        'keywords' : keyword,
        'abstract' : abstract,
        # 'pdf_name' : uuid,
        'highlight' : '',
        'lang' : lang,
        'search_site' : search_site
    }
    return data

def _acpcopernicus(page):
    '''
    :param page:
    :return:
    '''

    board_url = 'https://acp.copernicus.org'
    url = page.get('doi_url')
    # uuid = ''
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'
    soup = _fetch(url)

    title = soup.select_one('#page_content_container > div.article.abstract > h1').get_text().strip()
    abstract = soup.select_one('#page_content_container > div.article.abstract > div.abstract > p').get_text().strip()[10:]
    lang = _lang(abstract)

    keyword = page.get('keyword')
    if lang == 'eng':
        keyword = _korsplit(keyword)

    # if soup.select('div.content.text-center > a.pdf-icon'):
    #     pdf_url = board_url + soup.select_one('div.content.text-center > a.pdf-icon')['href']
    #     uuid = _pdfSave(pdf_url)
    # result = []
    data = {
        'rank' : page.get('rank'),
        'search_url' : page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title' : title,
        'author' : page.get('author'),
        'doi_url' : page.get('doi'),
        'keywords' : keyword,
        'abstract' : abstract,
        # 'pdf_name' : uuid,
        'highlight' : '',
        'lang' : lang,
        'search_site' : search_site
    }
    return data

def _amtcopernicus(page):
    board_url = 'https://amt.copernicus.org'
    url = page.get('doi_url')
    # uuid = ''
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'
    soup = _fetch(url)
    title = soup.select_one('#page_content_container > div.article.abstract > h1').get_text().strip()
    abstract = soup.select_one('#page_content_container > div.article.abstract > div.abstract > p').get_text().strip()[10:]
    lang = _lang(abstract)
    keyword = page.get('keyword')
    if lang == 'eng':
        keyword = _korsplit(keyword)
    # if soup.select('div.content.text-center > a.pdf-icon'):
    #     pdf_url = board_url + soup.select_one('div.content.text-center > a.pdf-icon')['href']
    #     uuid = _pdfSave(pdf_url)
    result = []
    data = {
        'rank' : page.get('rank'),
        'search_url' : page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title' : title,
        'author' : page.get('author'),
        'doi_url' : page.get('doi'),
        'keywords' : keyword,
        'abstract' : abstract,
        # 'pdf_name' : uuid,
        'highlight' : '',
        'lang' : lang,
        'search_site' : search_site
    }
    return data

def _mdpi(page):
    '''

    :param page:
    :return:
    '''
    board_url = 'https://www.mdpi.com'
    url = page.get('doi_url')
    # uuid = ''
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'
    soup = _fetch(url)
    title = soup.select_one('h1').get_text().strip().get_text().strip()
    abstract = soup.select_one('div.art-abstract.in-tab.hypothesis_container').get_text().strip()[10:]
    lang = _lang(abstract)
    keyword = page.get('keyword')
    if lang == 'eng':
        keyword = _korsplit(keyword)

    # if soup.select('div > a.button.button--color-inversed.margin-bottom-10.UD_ArticlePDF'):
    #     pdf_url = board_url + soup.select_one('div > a.button.button--color-inversed.margin-bottom-10.UD_ArticlePDF')['href']
    #     uuid = _pdfSave(pdf_url)
    result = []
    data = {
        'rank' : page.get('rank'),
        'search_url' : page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title' : title,
        'author' : page.get('author'),
        'doi_url' : page.get('doi'),
        'keywords' : keyword,
        'abstract' : abstract,
        # 'pdf_name' : uuid,
        'highlight' : '',
        'lang' : lang,
        'search_site' : search_site
    }
    return data

def _joie(page):
    board_url = 'http://fulltext.koreascholar.com/Service/Download.aspx?pdf='
    url = page.get('doi_url')
    # uuid = ''
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'
    soup = _fetch(url)
    title = soup.select_one('#engInfo > h1').get_text().strip()
    abstract = soup.select_one('#content > div.content_right > div.article_box > div.fulltext-wrap > div.ft-abstract > p').get_text().strip()
    lang = _lang(abstract)
    keyword = page.get('keyword')
    if search_site == 'scholar':
        keyword = ''
        if soup.soup.select('div.ft-keyword'):
            keyword = soup.select_one('div.ft-keyword').get_text().replace('\n','').replace('Key Words :','').strip()

    if lang == 'eng':
        keyword = _korsplit(keyword)
    # if soup.select('#content > div.content_right > div.article_box > div > a'):
    #     tag_name = soup.select_one('#content > div.content_right > div.article_box > div > a')['href']
    #     try:
    #         tag_number = tag_name.split("javascript:downloadPDF('")[1].split("');")[0]
    #         pdf_url = board_url + tag_number
    #         uuid = _pdfSave(pdf_url)
    #     except:
    #         pass
    data = {
        'rank' : page.get('rank'),
        'search_url' : page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title' : title,
        'author' : page.get('author'),
        'doi_url' : page.get('doi'),
        'keywords' : keyword,
        'abstract' : abstract,
        # 'pdf_name' : uuid,
        'highlight' : '',
        'lang' : lang,
        'search_site' : search_site
    }
    return data

def _nature(page):
    '''
    .pdf 붙이면 되는데 안되는놈들 있을 수 있음.
    :param url:
    :return:
    '''
    url = page.get('doi_url')
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'

    soup = _fetch(url)
    title = soup.select_one('#content > main > article > div.c-article-header > header > h1').get_text().strip()
    abstract = soup.select_one('#Abs1-content > p').get_text().strip()
    lang = _lang(abstract)
    keyword = page.get('keyword')

    if lang == 'eng':
        keyword = _korsplit(keyword)
    # pdf_url = url + '.pdf'
    # uuid = _pdfSave(pdf_url)
    data = {
        'rank' : page.get('rank'),
        'search_url' : page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title' : title,
        'author' : page.get('author'),
        'doi_url' : page.get('doi'),
        'keywords' : keyword,
        'abstract' : abstract,
        # 'pdf_name' : uuid,
        'highlight' : '',
        'lang' : lang,
        'search_site' : search_site
    }
    return data



def _sciencedirect(page):
    '''
     .pdf 붙이면 되는데 안되는놈들 있을 수 있음.
     :param url:
     :return:
     '''
    url = page.get('doi_url')
    url = url.split('https://linkinghub.elsevier.com/retrieve/')[1]
    url = 'https://www.sciencedirect.com/science/article/abs/' + url
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'
    highlight = ''
    soup = _fetch(url)
    title = soup.select_one('span.title-text').get_text().strip()
    abstract = soup.select_one('div.abstract.author > div').get_text().strip()
    lang = _lang(abstract)
    if soup.select('div.abstract.graphical > div > p'):
        highlight = soup.select_one('div.abstract.graphical > div > p').get_text()

    keyword = page.get('keyword')
    if search_site == 'scholar':
        keyword = ''
        if soup.select('div.Keywords.u-font-serif > div > div'):
            for i in soup.select('div.Keywords.u-font-serif > div > div'):
                keyword += ',' + i.get_text()
            keyword = keyword[1:]

    if lang == 'eng':
        keyword = _korsplit(keyword)
    pdf_url = url + '.pdf'
    # uuid = _pdfSave(pdf_url)
    data = {
        'rank': page.get('rank'),
        'search_url': page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title': title,
        'author': page.get('author'),
        'doi_url': page.get('doi'),
        'keywords': keyword,
        'abstract': abstract,
        # 'pdf_name': uuid,
        'highlight': highlight,
        'lang': lang,
        'search_site': search_site
    }
    return data


def _sciencedirectpage(page):
    '''
     .pdf 붙이면 되는데 안되는놈들 있을 수 있음.
     :param url:
     :return:
     '''
    url = page.get('doi_url')
    search_url = page.get('search_url')
    search_site = ''
    if 'https://academic.naver.com' in search_url:
        search_site = 'naver'
    elif 'https://scholar.google.co.kr/' in search_url:
        search_site = 'scholar'
    highlight = ''
    soup = _fetch(url)
    title = soup.select_one('span.title-text').get_text().strip()
    abstract = soup.select_one('div.abstract.author > div').get_text().strip()
    lang = _lang(abstract)
    if soup.select('div.abstract.graphical > div > p'):
        highlight = soup.select_one('div.abstract.graphical > div > p').get_text()

    keyword = page.get('keyword')
    if search_site == 'scholar':
        keyword = ''
        if soup.select('div.Keywords.u-font-serif > div > div'):
            for i in soup.select('div.Keywords.u-font-serif > div > div'):
                keyword += ',' + i.get_text()
            keyword = keyword[1:]

    if lang == 'eng':
        keyword = _korsplit(keyword)
    pdf_url = url + '.pdf'
    # uuid = _pdfSave(pdf_url)
    data = {
        'rank': page.get('rank'),
        'search_url': page.get('search_url'),
        'search_keyword': page.get('search_keyword'),
        'title': title,
        'author': page.get('author'),
        'doi_url': page.get('doi'),
        'keywords': keyword,
        'abstract': abstract,
        # 'pdf_name': uuid,
        'highlight': highlight,
        'lang': lang,
        'search_site': search_site
    }
    return data



def _csv_save(data, now, file_name, site):
    try:
        result = []
        result.append(data)
        dataframe = pd.DataFrame(result)
        if not os.path.exists(f'result/{site}_{now}_{file_name}.csv'):
            dataframe.to_csv(f"result/{site}_{now}_{file_name}.csv", mode='a', encoding='utf-8-sig', sep=",",
                             index=False)
        else:
            dataframe.to_csv(f"result/{site}_{now}_{file_name}.csv", mode='a', encoding='utf-8-sig', sep=",",
                             header=False, index=False)
    except Exception as e:
        logging.warning(f'{now}_{file_name}')
        logging.warning(f'save error : {e} / {data}')



def _txt_save(data, now, file_name, site):
    try:
        result = []
        result.append(data)
        dataframe = pd.DataFrame(result)
        if not os.path.exists(f'result/{site}_{now}_{file_name}.txt'):
            dataframe.to_csv(f"result/{site}_{now}_{file_name}.txt", index=False, sep=",")
        else:
            dataframe.to_csv(f'result/{site}_{now}_{file_name}.txt', mode='a+', index=False, header=None, sep=",")


    except Exception as e:
        logging.warning(f'{now}_{file_name}')
        logging.warning(f'save error : {e} / {data}')


def _korsplit(keyword):
    keyword = re.sub(u'[\u3130-\u318F\uAC00-\uD7A3]+', '', keyword)
    return keyword



def _lang(abstract):
    eng = 0
    kor = 0
    lang = 'eng'
    for txt in abstract:
        if 65 < ord(txt) and ord(txt) < 122:
            eng += 1
        hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', txt))
        kor += hanCount
        if eng < kor:
            lang = 'kor'

    return lang


# def _pdfSave(pdf_url):
#     uuid = str(uuid4()).replace('-','')
#     r = requests.get(pdf_url, stream=True)
#     chunk_size = 2000
#     path = os.getcwd()
#     with open(f'{path}/dags/result/{uuid}.pdf', 'wb', -1) as fd:
#         for chunk in r.iter_content(chunk_size):
#             fd.write(chunk)
#     return uuid