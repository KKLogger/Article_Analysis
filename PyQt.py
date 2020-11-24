import os
import sys

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup as bs
from makeImage import *
from myFunc import *
from nltk.tokenize import sent_tokenize

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
PATH = os.getcwd() + '\\'
# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType(PATH + "\\test.ui")[0]


# 화면을 띄우는데 사용되는 Class 선언


class WindowClass(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.searchBtn.clicked.connect(self.searchBtnFunction)

    def searchBtnFunction(self):
        try:
            highlights, abstract, keywords, lang = get_data()
            tokens = get_tokens(highlights + abstract + keywords, lang)
            sentences = sent_tokenize(highlights + abstract)

            search_keyword = self.keywordInput.text()
            if self.radioButton_1.isChecked() :
                crawl_site = 'Google'
            elif self.radioButton_2.isChecked() :
                crawl_site = 'Naver'
            else:
                print('Google 과 Naver 중 선택해주세요')
            print(search_keyword)
            # get_NG(tokens)
            # rank = get_association(search_keyword, tokens)
            return
            get_wordcloud(tokens)
            print(self.keywordInput.text())
            wordcloud = QPixmap(PATH + 'wordcloud.png')
            wordcloud = wordcloud.scaledToHeight(400)  # 사이즈가 조정
            self.label.setPixmap(wordcloud)
            if lang == "Eng":
                get_NG(sentences, lang)
                netgraph = QPixmap(PATH + 'networkgraph.png')
                netgraph = netgraph.scaledToHeight(400)  # 사이즈가 조정
                self.label_2.setPixmap(netgraph)
            else:
                pass
        except Exception as e:
            print(e)


def get_data():
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
        '•', ' ').replace('\xa0', '')
    abstract = soup.find('div', {'id': 'abs0015'}).text.replace('\xa0', '')
    keywords = soup.find_all('div', {'class': 'keyword'})
    keywords = [x.text.replace('\xa0', '') for x in keywords]
    keywords = " ".join(keywords)
    lang = "Eng"
    # text  = open('C:/Users/jlee/Downloads/미래로 가는 길.txt',encoding='euc-kr').read()
    # text.replace('\n','')
    # highlights = text
    # abstract = text
    # keywords = "안녕.그래"
    # lang = 'Kor'
    return highlights, abstract, keywords, lang


if __name__ == '__main__':
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
    # os.remove(PATH+'wordcloud.png')
