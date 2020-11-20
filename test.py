from nltk.tokenize import sent_tokenize
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Okt
import collections


text  = '''
안녕하세요. 저는 김형찬 입니다. 저도 안되었었는데 이제 되네요
'''

print(text)

okt = Okt()
sentence = sent_tokenize(text)

tokens = Kkma().morphs(text)

count_tokens = collections.Counter(tokens)
for token in tokens:
    print(token,count_tokens[token])

