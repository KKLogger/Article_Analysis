import pandas as pd
from myFunc import *
import time
start = time.time()

result = get_list('anythings','crawl_site')
print(time.time() - start)
print(result)