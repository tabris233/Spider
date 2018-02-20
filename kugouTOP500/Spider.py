import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# 解决乱码
import io
import sys
import urllib.request
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
res = urllib.request.urlopen('http://www.baidu.com')
htmlBytes = res.read()
print(htmlBytes.decode('utf-8'))

# 解决乱码结束

client = MongoClient()
songs = client.kugou_db.songs


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
 

def get_info(url):
    wb_data = requests.get(url,headers=headers)
    # wb_data.encoding = 'utf-8'
    soup = BeautifulSoup(wb_data.text,"lxml")
    ranks = soup.select(".pc_temp_num")
    titles = soup.select(".pc_temp_songlist > ul > li > a")
    song_times = soup.select(".pc_temp_time")

    for rank,title,song_time in zip(ranks,titles,song_times):
        data = {
            'rank': rank.get_text().strip(),
            'singer': title.get_text().split('-')[0].strip(),
            'song': title.get_text().split('-')[1].strip(),
            'time': song_time.get_text().strip()
        }
        print(data)
        song_id = songs.insert(data)  # insert db
        print(song_id)
        print('---------------------------------')

if __name__ == '__main__':
    urls = ['http://www.kugou.com/yy/rank/home/{}-8888.html'.format(str(i)) for i in range(1, 24)]
    for url in urls:
        # print(url)
        get_info(url)
        time.sleep(1)
        
        
