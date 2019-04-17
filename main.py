#!/usr/bin/env python2
# coding=utf-8

from bs4 import BeautifulSoup
import urllib2
import codecs
import time
import re
import sys, getopt
# https://github.com/aaronsw/html2text
import html2text

def deleteURL(s):
    ret = s[1:].split(']')[0]
    return ret

# responsible for printing
class PrintLayer(object):
    """docstring for PrintLayer"""
    def __init__(self, arg):
        super(PrintLayer, self).__init__()
        self.arg = arg

    @staticmethod
    def printWorkingPage(page):
        print "Work in Page " + str(page)

    @staticmethod
    def printWorkingArticle(article):
        print "Work in " + str(article)

    @staticmethod
    def printWorkingPhase(phase):
        if phase == 'getting-link':
            print "Phase 1: Getting the link"
        elif phase == 'export':
            print "Phase 2: Exporting"

    @staticmethod
    def printArticleCount(count):
        print 'Count of Articles: ' + str(count)

    @staticmethod
    def printOver():
        print 'All the posts has been downloaded. If there is any problem, feel free to file issues in https://github.com/gaocegege/csdn-blog-export/issues'


class Analyzer(object):
    """docstring for Analyzer"""
    def __init__(self):
        super(Analyzer, self).__init__()
    
    # get the page of the blog by url
    def get(self, url):
        headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
        req = urllib2.Request(url, headers=headers)
        html_doc = urllib2.urlopen(req).read()
        return html_doc

    # get the detail of the article
    def getContent(self, soup):
        return soup.find(class_='article-list')
        

class Exporter(Analyzer):
    """docstring for Exporter"""
    def __init__(self):
        super(Exporter, self).__init__()

    # get the title of the article
    def getTitle(self, detail):
        return detail.find(class_='article-header')

    # get the content of the article
    def getArticleContent(self, detail):
        return detail.find(id='article_content')

    def getHexoTitleMarkdown(self, detail):
        '''
        title: 面试学习.
        date: 2018-1-29 12:44:08
        categories:
        tags: [面试, C + +, 大数据, 操作系统, 计算机网络]  # 文章标签，可空，多标签请用格式，注意:后面有个空格
        description:
        toc: true
        '''

        title = '<' + \
                html2text.html2text(detail.find(class_='article-title-box').span.prettify()).rstrip('\n') + \
                '>' + \
                html2text.html2text(detail.find(class_='title-article').prettify()).rstrip('\n')
        date = html2text.html2text(detail.find(class_='time').prettify()).rstrip('\n')
        date = date[:4] + '-' + date[5:7] + '-' + date[8:10] + ' ' + date[-8:]
        # print('=' * 80 + '\n')
        # print(detail)
        # print(detail.find_all(class_='tag-link'))
        # print('=' * 80 + '\n')
        # print(detail.find_all(class_='tag-link'))
        tags = detail.find_all(class_='tag-link')
        # for tag in tags:
        #     tag = html2text.html2text(tag)
        #     print(tag)
        tags = map(deleteURL, map(lambda x: x.replace('\n', ''), map(html2text.html2text, map(lambda x: x.prettify(), tags))))
        print(tags)
        tags = ','.join(tags)
        # print(title, date, tags)
        str = u'''---
title: %s
date: %s
categories:
tags: [%s]  # 文章标签，可空，多标签请用格式，注意:后面有个空格
description:
toc: true
---

''' % (title, date, tags)
        # print(str)

        return str

    def spiderDate(self):
        return u'\n--- \n 博客爬取于`%s`\n***以下为正文***\n\n' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # export as markdown
    def export2markdown(self, f, detail):
        f.write(self.getHexoTitleMarkdown(detail))
        f.write('\n\n')
        f.write(html2text.html2text(self.getTitle(detail).prettify())[2:])
        f.write(self.spiderDate())
        f.write(html2text.html2text(self.getArticleContent(detail).prettify()))

    # export as html
    def export2html(self, f, detail):
        f.write(self.getTitle(detail).prettify())
        f.write(self.getArticleContent(detail).prettify())

    # export
    def export(self, link, filename, form):
        html_doc = self.get(link)
        soup = BeautifulSoup(html_doc, 'lxml')
        detail = soup.find(class_='blog-content-box')
        if form == 'markdown':
            f = codecs.open(filename + '.md', 'w', encoding='utf-8')
            self.export2markdown(f, detail)
            f.close()
            return
        elif form == 'html':
            f = codecs.open(filename + '.html', 'w', encoding='utf-8')
            self.export2html(f, detail)
            f.close()
            return

    def run(self, link, f, form):
        self.export(link, f, form)
        

class Parser(Analyzer):
    """docstring for parser"""
    def __init__(self):
        super(Parser, self).__init__()
        self.article_list = []
        self.page = -1

    # get the articles' link
    def parse(self, html_doc):
        soup = BeautifulSoup(html_doc, 'lxml')
        res = self.getContent(soup).find_all(class_='article-item-box csdn-tracking-statistics')[1:]
        # res = self.getContent(soup).find(class_='list_item_new').find(id='article_list').find_all(class_='article_item')
        i = 0
        for ele in res:
            self.article_list.append(ele.h4.a['href'])
            # self.article_list.append('http://blog.csdn.net/' + ele.find(class_='article_title').h1.span.a['href'])

    # get the page of the blog
    # may have a bug, because of the encoding
    def getPageNum(self, html_doc):
        self.page = 17
        return self.page
        soup = BeautifulSoup(html_doc, 'lxml')
        # papelist if a typo written by csdn front-end programmers?
        pageList = self.getContent(soup).find(id='papelist')
        # if there is only a little posts in one blog, the papelist element doesn't even exist
        if pageList == None:
        	print "Page is 1"
        	return 1
        res = pageList.span
        # get the page from text
        buf = str(res).split(' ')[3]
        strpage = ''
        for i in buf:
            if i >= '0' and i <= '9':
                strpage += i
        # cast str to int
        self.page =  int(strpage)
        return self.page

    # get all the link
    def getAllArticleLink(self, url):
    	# get the num of the page
        self.getPageNum(self.get(url))
        # iterate all the pages
        for i in range(1, self.page + 1):
            PrintLayer.printWorkingPage(i)
            self.parse(self.get(url + '/article/list/' + str(i)))

    # export the article
    def export(self, form):
        PrintLayer.printArticleCount(len(self.article_list))
        for link in self.article_list:
            PrintLayer.printWorkingArticle(link)
            exporter = Exporter()
            exporter.run(link, link.split('/')[6], form)

    # the page given
    def run(self, url, page=-1, form='markdown'):
        self.page = -1
        self.article_list = []
        PrintLayer.printWorkingPhase('getting-link')
        if page == -1:
            self.getAllArticleLink(url)
        else:
            if page <= self.getPageNum(self.get(url)):
                self.parse(self.get(url + '/article/list/' + str(page)))
            else:
                print 'page overflow:-/'
                sys.exit(2)
        PrintLayer.printWorkingPhase('export')
        self.export(form)
        PrintLayer.printOver()
    

def main(argv):
    page = -1
    directory = '-1'
    username = 'default'
    form = 'markdown'
    try:
        opts, args = getopt.getopt(argv,"hu:f:p:o:")
    except Exception, e:
        print 'main.py -u <username> [-f <format>] [-p <page>] [-o <outputDirectory>]'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -u <username> [-f <format>] [-p <page>] [-o <outputDirectory>]'
            sys.exit()
        elif opt == '-u':
            username = arg
        elif opt == '-p':
            page = arg
        elif opt == '-o':
            directory = arg
        elif opt == '-f':
            form = arg

    if username == 'default':
        print 'Err: Username err'
        sys.exit(2)
    if form != 'markdown' and form != 'html':
        print 'Err: format err'
        sys.exit(2)
    url = 'http://blog.csdn.net/' + username
    parser = Parser()
    parser.run(url, page, form)

if __name__ == "__main__":
   main(sys.argv[1:])