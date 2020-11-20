import collections
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.text import text_to_word_sequence
from nltk.tokenize import sent_tokenize
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Okt


def get_sentences(highlights, abstract):
    sentence = highlights + abstract
    sentences = sent_tokenize(sentence)
    sentences = [x.strip() for x in sentences]
    print(sentences)
    return sentences

def get_association(keyword, tokens,lang):
    if lang == "Eng":
        count_tokens = collections.Counter(tokens)
        keyword = keyword.lower()
    elif lang == "Kor":
        count_tokens = collections.Counter(tokens)
    return count_tokens[keyword]
def get_kr_stopwords():
    '''
    >>>input : x , 파일경로를 이용해 불용어 파일 읽기
    >>>output : 불용어 모음 리스트
    '''
    with open('article_analysis/Projects/한국어불용어.txt',encoding='utf-8') as f:
        stopwords = f.read()
    stopwords = stopwords.split(' ')[0]
    stopwords = stopwords.split('\n')
    return stopwords

def get_tokens(highlights, abstract, keywords,lang):
    tokens = list()
    if lang =="Eng":
        # 다른 토크나이징 함수
        # word_tokenize(highlights)
        # TreebankWordTokenizer().tokenize(highlights)
        # WordPunctTokenizer().tokenize(highlights)
        highlights_token = text_to_word_sequence(highlights)
        abstract_token = text_to_word_sequence(abstract)
        keywords_token = text_to_word_sequence(keywords)
        raw_tokens = highlights_token + abstract_token + keywords_token
        for token in raw_tokens:
            if token not in stopwords.words('english'):
                if len(token) > 2:
                    tokens.append(token)
    elif lang =="Kor":
        kr_stopwords = get_kr_stopwords()
        # sequence_tag = Okt()
        # sequence_tag = Hannanum()
        sequence_tag = Kkma()
        # print(highlights)

        highlights_token = sequence_tag.morphs(highlights)
        abstract_token = sequence_tag.morphs(abstract)
        keywords_token = sequence_tag.morphs(keywords)
        raw_tokens = highlights_token + abstract_token + keywords_token
        for token in raw_tokens:
            if token not in kr_stopwords:
                tokens.append(token)
    return tokens