import json
import math
import time

import pymongo
import requests

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

client = pymongo.MongoClient('localhost', 27017)
mydb = client['mydb']
lagou = mydb['lagou']
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Length': '26',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'JSESSIONID=ABAAABAACEBACDGBD96A0FDBF65899BEED0C2806FBAE0D3; _ga=GA1.2.1147332783.1519278311; _gid=GA1.2.417819532.1519278311; user_trace_token=20180222134511-8c14fa97-1793-11e8-8d16-525400f775ce; LGUID=20180222134511-8c14fdd9-1793-11e8-8d16-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; X_HTTP_TOKEN=2b1a3770cb4c023e7e6cea4bdafb3a2c; ab_test_random_num=0; hasDeliver=0; gate_login_token=""; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; LGSID=20180222135601-0fe171cb-1795-11e8-b085-5254005c3644; PRE_UTM=m_cf_cpt_baidu_pc; PRE_HOST=bzclk.baidu.com; PRE_SITE=http%3A%2F%2Fbzclk.baidu.com%2Fadrc.php%3Ft%3D06KL00c00f7Ghk60yUKm0FNkUsKEy34p00000PW4pNb00000IUnApW.THd_myIEIfK85yF9pywd0ZnquWNWnH7WPjDsnj0srADdPsKd5HbsPHm3nWRkPWKarH6dfWuDrj6vfYuan1wanbf4nHua0ADqI1YhUyPGujY1njn1nW0dn10YFMKzUvwGujYkP6K-5y9YIZK1rBtEILILQhk9uvqdQhPEUitOIgwVgLPEIgFWuHdVgvPhgvPsI7qBmy-bINqsmsKWThnqn1D1P0%26tpl%3Dtpl_10085_15730_11224%26l%3D1500117464%26attach%3Dlocation%253D%2526linkName%253D%2525E6%2525A0%252587%2525E9%2525A2%252598%2526linkText%253D%2525E3%252580%252590%2525E6%25258B%252589%2525E5%25258B%2525BE%2525E7%2525BD%252591%2525E3%252580%252591%2525E5%2525AE%252598%2525E7%2525BD%252591-%2525E4%2525B8%252593%2525E6%2525B3%2525A8%2525E4%2525BA%252592%2525E8%252581%252594%2525E7%2525BD%252591%2525E8%252581%25258C%2525E4%2525B8%25259A%2525E6%25259C%2525BA%2526xp%253Did%28%252522m6c247d9c%252522%29%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FH2%25255B1%25255D%25252FA%25255B1%25255D%2526linkType%253D%2526checksum%253D220%26ie%3DUTF-8%26f%3D8%26tn%3Dbaidu%26wd%3Dlagou%26oq%3Dlagou%26rqlang%3Dcn; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F%3Futm_source%3Dm_cf_cpt_baidu_pc; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519278312,1519278962; _putrc=040A28E70A548ABD; login=true; unick=%E8%91%A3%E5%85%A8; gate_login_token=1a1e1983405036b17cc8f912a542e5b147deb6b5dabcd247; LGRID=20180222135618-19b6e013-1795-11e8-8d18-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519278979; TG-TRACK-CODE=index_search; SEARCH_ID=3c1d978bd0f845ca917317c6bca3c948',
    'Host': 'www.lagou.com',
    'Origin': 'https://www.lagou.com',
    'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'X-Anit-Forge-Code': '0',
    'X-Anit-Forge-Token': 'None',
    'X-Requested-With': 'XMLHttpRequest'
}


def get_page(url, params):
    html = requests.post(url, data=params, headers=headers)
    json_data = json.loads(html.text)
    total_count = json_data['content']['positionResult']['totalCount']
    page_number = math.ceil(
        total_count/15) if math.ceil(total_count/15) < 30 else 30
    get_info(url, page_number)


def get_info(url, page):
    for pn in range(1, page+1):
        params = {
            'first': 'false',
            'pn': str(pn),
            'kd': 'Python'
        }
        try:
            html = requests.post(url, data=params, headers=headers)
            json_data = json.loads(html.text)
            results = json_data['content']['positionResult']['result']
            for result in results:
                infos = {
                    'businessZones': result['businessZones'],
                    'city': result['city'],
                    'companyFullName': result['companyFullName'],
                    'companyLabelList': result['companyLabelList'],
                    'companySize': result['companySize'],
                    'district': result['district'],
                    'education': result['education'],
                    'explain': result['explain'],
                    'financeStage': result['financeStage'],
                    'firstType': result['firstType'],
                    'formatCreateTime': result['formatCreateTime'],
                    'gradeDescription': result['gradeDescription'],
                    'imState': result['imState'],
                    'industryField': result['industryField'],
                    'jobNature': result['jobNature'],
                    'positionAdvantage': result['positionAdvantage'],
                    'salary': result['salary'],
                    'secondType': result['secondType'],
                    'workYear': result['workYear']
                }
                print('------------------')
                print(infos)
                lagou.insert_one(infos)
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            pass


if __name__ == "__main__":
    url = 'https://www.lagou.com/jobs/positionAjax.json'
    params = {
        'first': 'true',
        'pn': '1',
        'kd': 'python'
    }
    get_page(url, params)
