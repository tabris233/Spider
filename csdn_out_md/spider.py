#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-08-29 21:17:36
# @Author  : Kaiyan Zhang (kaiyanzh@outlook.com)
# @Link    : https://github.com/iseesaw
# @Version : v1.0
"""
将csdn博客导出为markdown
方法：
1. 编辑博客，抓包
2. 获取博客markdown格式链接
https://mp.csdn.net/mdeditor/getArticle?id=100125817
3. 模拟请求
Request Headers
:authority: bizapi.csdn.net
:method: GET
:path: /blog-console-api/v1/article/getQueryCriteriaNew
:scheme: https
accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7
cookie: uuid_tt_dd=10_9923125910-1585743227120-322102; dc_session_id=10_1585743227120.934232; _ga=GA1.2.536173610.1585815737; UserName=qq_33184171; UserInfo=aee18eac8bfe4df4a96704e8c1bdd168; UserToken=aee18eac8bfe4df4a96704e8c1bdd168; UserNick=Tabris_; AU=54F; UN=qq_33184171; BT=1588581483957; p_uid=U000000; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_9923125910-1585743227120-322102!5744*1*qq_33184171; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22qq_33184171%22%2C%22scope%22%3A1%7D%7D; dc_sid=0dfd33c619d4bcb40b2f43d23f3cb9e3; announcement=%257B%2522isLogin%2522%253Atrue%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Flive.csdn.net%252Froom%252Fbjchenxu%252FvVsg8RCt%2522%252C%2522announcementCount%2522%253A1%252C%2522announcementExpire%2522%253A258044919%257D; _gid=GA1.2.437537726.1591763590; c_adb=1; c_first_ref=www.google.com; c_utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-9.nonecase; c_first_page=https%3A//blog.csdn.net/qq_36962569/article/details/100167955; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1591769767,1591779463,1591779574,1591779596; c_ref=https%3A//blog.csdn.net/qq_33184171/article/details/51066516; dc_tos=qbpde2; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1591780107
origin: https://mp.csdn.net
referer: https://mp.csdn.net/console/article
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-site
user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36
x-ca-key: 203803574
x-ca-nonce: 3daf3bfc-736c-41d3-aa88-d1359cefcc3c
x-ca-signature: jn3nfJ0rWFAo0Xmfi7KpViUTWs6C5MdJc61PAC89xxk=
x-ca-signature-headers: x-ca-key,x-ca-nonce
"""
import json
import uuid
import time
import requests
import datetime
from bs4 import BeautifulSoup

yaml = u'''---
title: "{title}"
date: {date}
description:
toc: true
author: tabris
# 图片推荐使用图床(腾讯云、七牛云、又拍云等)来做图片的路径.如:http://xxx.com/xxx.jpg
img:
# 如果top值为true，则会是首页推荐文章
top: false
# 如果要对文章设置阅读验证密码的话，就可以在设置password的值，该值必须是用SHA256加密后的密码，防止被他人识破
password:
# 本文章是否开启mathjax，且需要在主题的_config.yml文件中也需要开启才行
mathjax: false
summary: "{description}"
categories: {categories}
tags: {tags}
key: {key}
---

'''

def request_blog_list(page=1):
    """获取博客列表
    主要包括博客的id以及发表时间等
    """
    url = f'https://blog.csdn.net/qq_33184171/article/list/{page}'
    print(url)
    reply = requests.get(url)
    parse = BeautifulSoup(reply.content, "lxml")
    spans = parse.find_all('div', attrs={'class':'article-item-box csdn-tracking-statistics'})
    blogs = []
    for span in spans:
        # print(span)
        # print('*'*80)
        try:
            _blank = span.find('a', attrs={'target':'_blank'})
            abstract = _blank.get_text()
            href = _blank['href']
            read_num = span.find('span', attrs={'class':'read-num'}).get_text()
            date = span.find('span', attrs={'class':'date'}).get_text()
            blog_id = href.split("/")[-1]
            blogs.append([blog_id, date, read_num, abstract])
        except:
            print('Wrong, ' + href)
    return blogs


def request_md(blog_id, blog_info):
    """获取博客包含markdown文本的json数据"""
    url = f"https://blog-console-api.csdn.net/v1/editor/getArticle?id={blog_id}"
    headers = {
        "cookie": "uuid_tt_dd=10_9923125910-1585743227120-322102; dc_session_id=10_1585743227120.934232; _ga=GA1.2.536173610.1585815737; UserName=qq_33184171; UserInfo=aee18eac8bfe4df4a96704e8c1bdd168; UserToken=aee18eac8bfe4df4a96704e8c1bdd168; UserNick=Tabris_; AU=54F; UN=qq_33184171; BT=1588581483957; p_uid=U000000; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_9923125910-1585743227120-322102!5744*1*qq_33184171; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22qq_33184171%22%2C%22scope%22%3A1%7D%7D; dc_sid=0dfd33c619d4bcb40b2f43d23f3cb9e3; announcement=%257B%2522isLogin%2522%253Atrue%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Flive.csdn.net%252Froom%252Fbjchenxu%252FvVsg8RCt%2522%252C%2522announcementCount%2522%253A1%252C%2522announcementExpire%2522%253A258044919%257D; _gid=GA1.2.437537726.1591763590; c_first_ref=www.google.com; c_utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-9.nonecase; aliyun_webUmidToken=T2gAH3dNncDq+XdWayVvC+ryaCqcDA9GlxWr6WauHpW0mulwJOzirvXiwbqVGMPAV6mts4FuxKDG3b2o64fi9GHB; c_first_page=https%3A//blog.csdn.net/zcmlimi/article/details/47709049; c_ref=https%3A//www.google.com/; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1591779463,1591779574,1591779596,1591789117; c_adb=1; dc_tos=qbpkhb; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1591789296",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }
    data = {"id": blog_id}
    try:
        reply = requests.get(url, headers=headers, data=data)
    except Exception as e:
        try:
            reply = requests.get(url, headers=headers, data=data)
        except Exception as e:
            reply = requests.get(url, headers=headers, data=data)
            exit(1)

    try:
        write_hexo_md(reply.json(), blog_info)
    except Exception as e:
        print("***********************************")
        print(e)
        exit(1)
        #print(reply.json())


def write_hexo_md(data, blog_info):
    """将获取的json数据解析为hexo的markdown格式"""

    title       = blog_info[-1] + data["data"]["title"]
    description = data["data"]["description"]

    tags       = "[CSDN," + data["data"]["tags"] + "]"
    categories = "[CSDN," + data["data"]["categories"].replace("=", "") + "]"

    # 页面唯一标识符，用于统计系统和评论系统
    key = "key" + str(uuid.uuid4())

    header = yaml.format(title=title,
                         date=blog_info[1],
                         description="",
                         categories=categories,
                         tags=tags,
                         key=key,
                         read_num=blog_info[2])

    content = data["data"]["markdowncontent"].replace("@[toc]", "").replace("\n######", "\n###### ").replace("\n#####" , "\n##### ").replace("\n####"  , "\n#### ").replace("\n###"   , "\n### ").replace("\n##"    , "\n## ").replace("\n#"     , "\n# ").replace("# # # # # #"     , "######").replace("# # # # #"     , "#####").replace("# # # #"     , "####").replace("# # #"     , "###").replace("# #"     , "##")

    name = "{date}-{blog_id}".format(date=blog_info[1].split(" ")[0], blog_id=blog_info[0])
    with open(f"./blogs/{name}.md", "w", encoding="utf-8") as f:
        f.write(header + content)

    print(f"写入 {name}")


def get_blog_id(total_pages=3):
    """
    获取博客列表，包括id，时间
    获取博客markdown数据
    保存hexo格式markdown
    """
    blogs = []
    for page in range(1, total_pages + 1):
        blogs.extend(request_blog_list(page))

    for blog in blogs:
        print(blog, end=",\n")

    return blogs

def main(blogs):
    for blog_info in blogs:
        blog_id = blog_info[0]
        request_md(blog_id, blog_info)
        time.sleep(1)

if __name__ == '__main__':
    blogs = get_blog_id(9)
    main(blogs)