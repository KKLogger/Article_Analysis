import requests
from bs4 import BeautifulSoup as bs


def get_strpart(str, start, end):
    if len(end) == 0:
        result = str[str.index(start) + len(start):]
    else:
        result = str[str.index(start) + len(start):  str.index(end)]
    return result


urls = list()
page = 190
while True:
    print(page)
    response = requests.get(
        'https://academic.naver.com/search.naver?field=0&docType=1&query=h2o&page={page}'.format(page=page))
    if response.status_code == 500:
        page += 1
        continue
    soup = bs(response.text, 'lxml')
    print(soup.find('div', {'class': 'ui_paging_small'}
                    ).find_all('a')[-1].get('_pageno'))
    if soup.find('div', {'class': 'ui_paging_small'}).find_all('a')[-1].get('_pageno') == page:
        break
    article_list = soup.find_all('div', {'class': 'ui_listing_info'})
    for article in article_list:
        doc_id = get_strpart(article.find('h4').find(
            'a').get('href'), '?doc_id=', '')
        response = requests.get(
            'https://academic.naver.com/article.naver?doc_id={doc_id}'.format(doc_id=doc_id))
        soup = bs(response.text, 'lxml')
        try:
            doc_url = [x.find('a', {'target': '_blank'})for x in soup.find('dl', {'class': 'ui_listdetail_list'}).find_all(
                'dd', {'class': 'ui_listdetail_item_info'})][-1].get('href')
        except:
            continue
        urls.append(doc_url)
    page += 1
