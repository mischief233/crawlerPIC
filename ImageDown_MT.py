# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 17:55:42 2023
优化版v1.0 by AI on Mon Apr 4 14:39:06 2023
@author: jinqiu
"""

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
import multiprocessing


class ImageDownloader:
    def download_bing_image(self, keyword, save_dir):
        header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36'
            }
        
        url = "https://cn.bing.com/images/async?q={0}&first={1}&count={2}&scenario=ImageBasicHover&datsrc=N_I&layout=ColumnBased&mmasync=1&dgState=c*9_y*2226s2180s2072s2043s2292s2295s2079s2203s2094_i*71_w*198&IG=0D6AD6CBAF43430EA716510A4754C951&SFX={3}&iid=images.5599"
        
        #需要爬取的图片关键词
        name=keyword
        #本地存储路径
        path = save_dir

        '''获取缩略图列表页'''
        def getStartHtml(url,key,first,loadNum,sfx):
            page = urllib.request.Request(url.format(key,first,loadNum,sfx),headers = header)
            html = urllib.request.urlopen(page)
            return html
        
        '''从缩略图列表页中找到原图的url，并返回这一页的图片数量'''
        def findImgUrlFromHtml(html,rule,url,key,first,loadNum,sfx,count):
            soup = BeautifulSoup(html,"lxml")
            link_list = soup.find_all("a", class_="iusc")
            url = []
            for link in link_list:
                result = re.search(rule, str(link))
                #将字符串"amp;"删除
                url = result.group(0)
                #组装完整url
                url = url[8:len(url)]
                #打开高清图片网址
                getImage(url,count,name,path)
                count+=1
            #完成一页，继续加载下一页
            return count
        
        '''从原图url中将原图保存到本地'''
        def getImage(url,count,name,path):
            try:
                time.sleep(0.5)
                urllib.request.urlretrieve(url,path+'/bing_'+name+str(count+1)+'.jpg')
            except Exception :
                time.sleep(1)
#                 print("产生了一点点错误，跳过...")

        key = urllib.parse.quote(name)
        first = 1
        loadNum = 50
        sfx = 1
        count = 0
        #正则表达式
        rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")
        #图片保存路径
        if not os.path.exists(path):
            os.makedirs(path)
        #抓500张好了
        while count<20000:
            html = getStartHtml(url,key,first,loadNum,sfx)
            count += findImgUrlFromHtml(html,rule,url,key,first,loadNum,sfx,count)
            first = count+1
            sfx += 1
        # print(f'必应图片爬取关键词{name},共爬取{sfx}张图片！')

    def download_baidu_image(self, keyword, save_dir):
        num = 0
        numPicture = 0
        file = ''

        def Find(url, A):
            List = []
            t = 0
            i = 1
            s = 0
            while t < 1000:
                Url = url + str(t)
                try:
                    # 这里搞了下
                    Result = A.get(Url, timeout=7, allow_redirects=False)
                except BaseException:
                    t = t + 60
                    continue
                else:
                    result = Result.text
                    pic_url = re.findall('"objURL":"(.*?)",', result, re.S)  # 先利用正则表达式找到图片url
                    s += len(pic_url)
                    if len(pic_url) == 0:
                        break
                    else:
                        List.append(pic_url)
                        t = t + 60
            return s


        def recommend(url):
            Re = []
            try:
                html = requests.get(url, allow_redirects=False)
            except error.HTTPError as e:
                return
            else:
                html.encoding = 'utf-8'
                bsObj = BeautifulSoup(html.text, 'html.parser')
                div = bsObj.find('div', id='topRS')
                if div is not None:
                    listA = div.findAll('a')
                    for i in listA:
                        if i is not None:
                            Re.append(i.get_text())
                return Re

        def dowmloadPicture(html, keyword,save_dir):
            num = 0
            # t =0
            pic_url = re.findall('"objURL":"(.*?)",', html, re.S)  # 先利用正则表达式找到图片url
            for each in pic_url:
                try:
                    if each is not None:
                        pic = requests.get(each, timeout=7)
                    else:
                        continue
                except BaseException:
#                     print('错误，当前图片无法下载')
                    continue
                else:
                    string = save_dir + r'/baidu_' + keyword + '_' + str(num) + '.jpg'
                    fp = open(string, 'wb')
                    fp.write(pic.content)
                    fp.close()
                    num += 1
                if num >= numPicture:
                    return
        ##############################
        # 这里加了点
        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Upgrade-Insecure-Requests': '1'
        }

        A = requests.Session()
        A.headers = headers
    ###############################

        word = keyword
        # add = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=%E5%BC%A0%E5%A4%A9%E7%88%B1&pn=120'
        url = 'https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + word + '&pn='

        # 这里搞了下
        tot = Find(url, A)
        Recommend = recommend(url)  # 记录相关推荐
        # print('百度图片关键词%s，共有%d张图片！' % (word, tot))
        numPicture = tot
        file = save_dir
        t = 0
        tmp = url
        while t < numPicture:
            try:
                url = tmp + str(t)

                # 这里搞了下
                result = A.get(url, timeout=10, allow_redirects=False)
            except error.HTTPError as e:
                print('网络错误，请调整网络后重试')
                t = t + 60
            else:
                dowmloadPicture(result.text, word, save_dir)
                t = t + 60

        print('关键词搜索结束！')

    def generate_synonyms_keyword_list(self,keyword1, keyword2):
        synonyms_keywords_1 = []
        synonyms_keywords_1.extend(keyword1)
        for i in keyword1:
            keywords = set(synonyms.nearby(i)[0])
            synonyms_keywords_1.extend(keywords)
        synonyms_keywords_2 = keyword2

        keywords_combined = []
        for kw1 in synonyms_keywords_1:
            for kw2 in synonyms_keywords_2:
                keywords_combined.append(kw1 + kw2)
                keywords_combined.append(kw2 + kw1)

        return keywords_combined
    

    def jiebalist(self,keyword):
        words = jieba.lcut(keyword)
        if len(words)==2:
            return [words[0]],[words[1]]
        else:
            print('请确保输入词语结构为词+词，如垃圾楼道！')
    
    def pre_run(self,keyword1, keyword2):
        keywords = self.generate_synonyms_keyword_list(keyword1, keyword2)
        return keywords
    
    def pcMT(self,keyword, save_dir):
        print(f'现在开始爬关键词《{keyword}》！下面开始从必应图片爬！')
        try:
            self.download_bing_image(keyword, save_dir)
        except:
            pass
        aa = len(os.listdir(save_dir))
        print(f'必应图片一共抓取到{aa}张图片！下面开始从百度图片爬！')
        try:
            self.download_baidu_image(keyword, save_dir)
        except Exception as e:
            print(e)
        aa = len(os.listdir(save_dir))
        print(f'关键词《{keyword}》抓取到{aa}张图片！')
    
    def run(self, keywords, save_dir,is_adj = False):
        if is_adj:
            keyword1, keyword2 = self.jiebalist(keywords)
            keywords = self.generate_synonyms_keyword_list(keyword1, keyword2)
        else:
            print('请确保已经清洗了关键词库！')
        for keyword in tn(keywords):
            print(f'现在开始爬关键词《{keyword}》！下面开始从必应图片爬！')
            try:
                self.download_bing_image(keyword, save_dir)
            except Exception as e:
                print(e)
                pass
            aa = len(os.listdir(save_dir))
            print(f'必应图片一共抓取到{aa}张图片！下面开始从百度图片爬！')
            try:
                self.download_baidu_image(keyword, save_dir)
            except:
                pass
            aa = len(os.listdir(save_dir))
            print(f'关键词《{keyword}》抓取到{aa}张图片！')
        bb = len(os.listdir(save_dir))
        print(f'一共抓取到{bb}张图片！下面开始清洗图片！')
        result = os.system('find ./ -size -1k -name "*.jpg" | xargs rm')
        if result:
            print(result)
        print('下面开始打包发给你哟！')
        result = os.system(f'zip -r result.zip {save_dir}')
        print('全部结束啦')

    def runMT(self, keywords, save_dir,is_adj = False):
        if is_adj:
            keyword1, keyword2 = self.jiebalist(keywords)
            keywords = self.generate_synonyms_keyword_list(keyword1, keyword2)
        else:
            print('请确保已经清洗了关键词库！')
        
        pool = multiprocessing.Pool(processes=10)
        for keyword in tn(keywords):
            pool.apply_async(self.pcMT, (keyword, save_dir))
        pool.close()
        pool.join()

        bb = len(os.listdir(save_dir))
        print(f'一共抓取到{bb}张图片！下面开始清洗图片！')
        result = os.system('find ./ -size -1k -name "*.jpg" | xargs rm')
        if result:
            print(result)
        print('下面开始打包发给你哟！')
        result = os.system(f'zip -r result.zip {save_dir}')
        print('全部结束啦')
