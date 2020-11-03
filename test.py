import requests
from bs4 import BeautifulSoup as bs
import lxml


def get_association(keyword, tokens):
    import collections
    count_tokens = collections.Counter(tokens)
    keyword = keyword.lower()
    return count_tokens[keyword]


def get_tokens(highlights, abstract, keywords):

    from tensorflow.keras.preprocessing.text import text_to_word_sequence
    # 다른 토크나이징 함수
    # word_tokenize(highlights)
    # TreebankWordTokenizer().tokenize(highlights)
    # WordPunctTokenizer().tokenize(highlights)

    highlights_token = text_to_word_sequence(highlights)
    abstract_token = text_to_word_sequence(abstract)
    keywords_token = text_to_word_sequence(keywords)
    raw_tokens = highlights_token + abstract_token + keywords_token

    tokens = list()
    from nltk.corpus import stopwords
    for token in raw_tokens:
        if token not in stopwords.words('english'):
            if len(token) > 2:
                tokens.append(token)
    return tokens


def get_wordcloud(tokens):
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    wordcloud = WordCloud(background_color='white').generate(" ".join(tokens))
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='lanczos')
    plt.axis('off')
    # plt.show()


def get_NG(tokens):
    import plotly.offline as py
    import plotly.graph_objects as go
    import networkx as nx
    import collections
    count_tokens = collections.Counter(tokens)
    print(count_tokens)


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
    '•', '').replace('\xa0', '')
abstract = soup.find('div', {'id': 'abs0015'}).text.replace('\xa0', '')
keywords = soup.find_all('div', {'class': 'keyword'})
keywords = [x.text.replace('\xa0', '') for x in keywords]
keywords = " ".join(keywords)
search_keyword = 'mno2'
tokens = get_tokens(highlights, abstract, keywords)
get_NG(tokens)
# rank = get_association(search_keyword, tokens)
# get_wordcloud(tokens)
