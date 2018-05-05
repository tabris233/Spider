# 爬取CSDN数据文件

# 还没有解决= {
#     'ajax': '',
#     '去重': [
#         '暴力插入到HASH中',
#         '在爬取阶段只访问之前没有访问过的：但是如果ip在变 如何知道哪些之前爬过？',
#     ],
#     '代理-防止被封ip':NULL,
# }

# -*- coding: utf-8 -*-

import time  # 引入time模块  使用time()函数

import redis
import requests
from bs4 import BeautifulSoup

# 解决乱码
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
# 解决乱码结束

r = redis.Redis(host='localhost', port=6379, decode_responses=True, db=2)

def insert(info,time):
    id = hash(info+':'+time)
    print(id,info+':'+time)
    r.hset('CSDN',id,info+':'+time)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}

def get_time(_url):
    wb_data = requests.get(_url, headers=headers)
    # wb_data.encoding = 'utf-8'
    soup = BeautifulSoup(wb_data.text, "lxml")
    time = soup.select('.time')
    for x in time:
        # print(x)
        return x.text

def get_info(url):
    wb_data = requests.get(url, headers=headers)
    # wb_data.encoding = 'utf-8'
    soup = BeautifulSoup(wb_data.text, "lxml")
    titles = soup.select('a[strategy="new"]')

    for title in titles:
        _url = title.get('href')  # 获取这个博文的链接 访问得到time
        time = get_time(_url)     
        info = title.text.strip() 
        insert(info,time)         # 插入到redis数据库中
    
    # 测试用的
    # print(type(soup))
    # print(" ---------------------------- ")
    # print(" ---------------------------- ")
    # print(" ---------------------------- ")
    # print(" ---------------------------- ")
    # print(soup.prettify())
    # print(soup.title.string)
    # print('Successfully!')


if __name__ == '__main__':
    url = 'https://blog.csdn.net/nav/cloud'
    # while(true):
    get_info(url)
    # time.sleep(60)  # 休眠1s
