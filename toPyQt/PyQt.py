import os
import sys
import webbrowser
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from bs4 import BeautifulSoup as bs
from makeImage import *
from myFunc import *
from nltk.tokenize import sent_tokenize

PATH = os.getcwd() + "\\"
# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType(PATH + "\\test.ui")[0]


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.searchBtn.clicked.connect(self.searchBtnFunction)
        self.listWidget.itemClicked.connect(self.chkItemClicked)
        self.pushButton.clicked.connect(self.pushButtonClicked)
    def closeEvent(self, event):
        self.deleteLater()
    def pushButtonClicked(self):
        webbrowser.open(self.cur_article["doi_url"])

    def chkItemClicked(self):
        try:
            title = self.listWidget.currentItem().text()
            for article in self.article_list:
                if article["title"] == title:
                    self.cur_article = article
            self.authorName.setText(self.cur_article["author"])
            highlights = self.cur_article["highlight"]
            abstract = self.cur_article["abstract"]
            keywords = self.cur_article["keywords"]
            lang = self.cur_article["lang"]
            tokens = self.cur_article["tokens"]
            sentences = self.cur_article["sentences"]
            get_wordcloud(tokens)
            wordcloud = QPixmap(PATH + "result/wordcloud.png")
            wordcloud = wordcloud.scaledToHeight(400)  # 사이즈가 조정
            self.label.setPixmap(wordcloud)
            if lang == "eng":
                get_NG(sentences, lang)
                netgraph = QPixmap(PATH + "result/networkgraph.png")
                netgraph = netgraph.scaledToHeight(400)  # 사이즈가 조정
                self.label_2.setPixmap(netgraph)
            else:
                self.label_2.setText("아직 한국어는 지원하지 않습니다.")
        except Exception as e:
            print(f"error : {e}")

    def searchBtnFunction(self):
        search_keyword = self.keywordInput.text()
        if self.radioButton_1.isChecked():
            crawl_site = "Google"
        elif self.radioButton_2.isChecked():
            crawl_site = "Naver"
        else:
            print("Google 과 Naver 중 선택해주세요")
        max_num = self.numInput.text()
        if max_num == "":
            max_num = 1000
        else :
            max_num = int(max_num)
        self.article_list = get_list(search_keyword, crawl_site,max_num)
        for row_num in range(len(self.article_list)):
            self.listWidget.addItem(self.article_list[row_num]["title"])
        ##################################################
        # try:
        #     search_keyword = self.keywordInput.text()
        #     if self.radioButton_1.isChecked():
        #         crawl_site = "Google"
        #     elif self.radioButton_2.isChecked():
        #         crawl_site = "Naver"
        #     else:
        #         print("Google 과 Naver 중 선택해주세요")
        #     self.article_list = get_list(search_keyword, crawl_site)
        #     for row_num in range(len(self.article_list)):
        #         self.listWidget.addItem(self.article_list[row_num]["title"])
        # except Exception as e:
        #     print(f"error : {e}")
        return


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
    # os.remove(PATH+'wordcloud.png')
