# crawlerPIC
##从必应图片与百度图片中爬取图片并保存

### 依赖库
```python
import sys
import os
import urllib
from bs4 import BeautifulSoup
import re
import time
import requests
from urllib import error
import synonyms
import jieba
from tqdm.auto import tqdm as tn
```

### 调用方法
1. 单个线程
```python
import ImageDown
aa = ImageDown.ImageDownloader()
#cy1为自定义词库
cy1 = []
aa.runMT(cy1,'./楼道20230404/bad')
```

2. 多个线程
```python
import ImageDown_MT
aa = ImageDown_MT.ImageDownloader()
#cy1为自定义词库
cy1 = []
aa.runMT(cy1,'./楼道20230404/bad')
```

### 支持功能
1. 同义词扩展
2. 多线程爬图
3. 自定义词库爬图
4. 同义词筛选
5. 自动清洗脏图片
6. 自动压缩并保存
