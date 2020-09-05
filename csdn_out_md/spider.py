#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-08-29 21:17:36
# @Author  : Kaiyan Zhang (kaiyanzh@outlook.com)
# @Link    : https://github.com/iseesaw
# @Version : v1.0

import json
import uuid
import time
import requests
import datetime
from bs4 import BeautifulSoup

import blogs_list

yaml = u'''---
title: "{title}"
date: {date}
toc: true
author: tabris
summary: "{description}"
categories: {categories}
mathjax: true # false: 不渲染, true: 渲染, internal: 只在文章内部渲染，文章列表中不渲染
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
        "cookie": "TODO 在此填入cookie",
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

    title       = "[" + blog_info[-1] + "]" + data["data"]["title"]
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

    # spider_date = u'\n--- \n 博客爬取于`%s`\n***以下为正文***\n\n' %

    content = data["data"]["markdowncontent"].replace("@[toc]", "").replace("\n######", "\n###### ").replace("\n#####" , "\n##### ").replace("\n####"  , "\n#### ").replace("\n###"   , "\n### ").replace("\n##"    , "\n## ").replace("\n#"     , "\n# ").replace("# # # # # #"     , "######").replace("# # # # #"     , "#####").replace("# # # #"     , "####").replace("# # #"     , "###").replace("# #"     , "##")

    name = "{date}-{blog_id}".format(date=blog_info[1].split(" ")[0], blog_id=blog_info[0])

    posts_top = '''# {title}

{create_time}  [Tabris_](https://me.csdn.net/qq_33184171) 阅读数：{read_num}

---

博客爬取于`{date}`
***以下为正文***

版权声明：本文为Tabris原创文章，未经博主允许不得私自转载。
https://blog.csdn.net/qq_33184171/article/details/{blog_id}

<!-- more -->

---

'''.format(title=title,
               create_time=blog_info[1],
               date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
               read_num=blog_info[2],
               blog_id=blog_info[0])

    with open(f"./blogs/{name}.md", "w", encoding="utf-8") as f:
        f.write(header)
        f.write(posts_top)
        f.write(content)

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
    # blogs = get_blog_id(9)
    main(blogs_list.blogs_list)
