# 爬取CSDN数据文件

# 环境
# Anaconda3      python 环境
# redis          python操作redis的库
# requests       访问网页用的
# BeautifulSoup  HTML解析库

# 插入redis时采用HASH
# key:field:value => CSDN:hash(title+':'+time):[title+':'+time]

# 直接在html中解析出title
# 由于server返回的json也没有时间,所以对每个title访问其文章所在网页获取时间

# -*- coding: utf-8 -*-

import time  # 引入time模块  使用time()函数

import redis
import requests
from bs4 import BeautifulSoup

SCHEDULE = True

r = redis.Redis(host='localhost', port=6379, decode_responses=True, db=2)

def insert(key,info,time):
    id = hash(info+':'+time)
    if r.hexists(key, id):
        pass
    else:
        print(id,':\n',info+':'+time)
        r.hset(key, id, info+':'+time)
        if(SCHEDULE): print('---------------->>>>数据已插入redis数据库\n')

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'uuid_tt_dd=10_19746667890-1517545658385-746207; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=1788*1*PC_VC; kd_user_id=232eab61-645a-4aa5-a31b-eb326ea4199a; UN=qq_33184171; __yadk_uid=OonBfwi6PAqK1J5FXPDtCMNEZORRQdE7; __message_sys_msg_id=0; __message_gu_msg_id=0; __message_cnel_msg_id=0; __message_in_school=0; dc_session_id=10_1525407336381.331877; smidV2=20180504121546487688887a90d7cb34e4f8bda3060fd4003ebe7b21de7fc00; kd_0e1a1f29-37da-4c44-8a33-b4735dc85f10_kuickDeal_pageIndex=0; kd_0e1a1f29-37da-4c44-8a33-b4735dc85f10_kuickDeal_leaveTime=1525407376813; BT=1525407375396; ADHOC_MEMBERSHIP_CLIENT_ID1.0=49a3019b-b278-a70a-9bef-bbd1832e4634; TY_SESSION_ID=3f5f4a07-df4b-4136-b4bd-c0cd2c99ff1d; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1525497563,1525498773,1525499121,1525505588; dc_tos=p88vy0; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1525505993',
    'Host': 'blog.csdn.net',
    'Referer': 'https://blog.csdn.net/nav/cloud',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'X-Tingyun-Id': 'wl4EtIR_7Is;r=505993350',
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
    if (SCHEDULE): print('----------------------')
    if (SCHEDULE): print('开始访问网站')
    wb_data = requests.get(url, headers=headers)
    # wb_data.encoding = 'utf-8'
    soup = BeautifulSoup(wb_data.text, "lxml")

    if(SCHEDULE): print('访问成功,准备爬取数据')

    titles = soup.select('a[strategy="new"]')
    titles.extend(soup.select('a[strategy="hot"]'))
    for title in titles:
        _url = title.get('href')  # 获取这个博文的链接 访问得到time
        time = get_time(_url)     
        info = title.text.strip() 
        insert('CSDN', info, time)         # 插入到redis数据库中

    if(SCHEDULE): print('爬取数据成功')

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
    while(True):
        get_info(url)
        time.sleep(10)  # 休眠10s
    
    print('PROGRAM END')
