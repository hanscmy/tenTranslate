#!/usr/bin/env python
# coding: utf-8
import random
import re
import time
import requests
from traceback import print_exc
import json
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",
]
def get_filter(text):
    
    if isinstance(text, list):
        text = ''.join(text)
    text = str(text)
    text = text.strip()
    filter_list = [
        '\r', '\n', '\t', '\u3000', '\xa0', '\u2002',
        '<br>', '<br/>', '    ', '  ', '&nbsp;', '>>', '&quot;',
        '展开全部', ' '
    ]
    for fl in filter_list:
        text = text.replace(fl, '')
    return text


def get_qtv_qtk():
    num = 0
    while True:
        api_url = 'https://fanyi.qq.com/'

        headers = {
            'User-Agent': USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)], }

        res = requests.get(api_url, headers=headers)
        fy_guid = res.cookies.get('fy_guid')

        data = res.text
        reg = re.compile(r'reauthuri = "(.*?)"')
        uri = reg.search(data)
        if not uri:
            num += 1
            continue
        uri = uri.group(1)
        api_url = 'https://fanyi.qq.com/api/' + uri

        res = requests.post(api_url, None, headers=headers)

        if not res or not res.text:
            continue
        json_res = json.loads(res.text)
        qtv = json_res["qtv"]
        qtk = json_res["qtk"]
        # print("我尝试连接了"+str(num)+"次")
        return fy_guid, qtv, qtk


def getHtml(url,headers,data):

    try:
        html= requests.post(url=url,data= data,headers=headers)
        datas = html.json()['translate']['records']
        trans_result = ''.join([data['targetText'] for data in datas])

    except Exception:
        # print_exc()
        trans_result = '1331'

    return trans_result


class TencentTrans(object):
    
    def __init__(self):
        self.time = time.time()

        self.api_url = 'https://fanyi.qq.com/api/translate'
        self.headers = {
            'Cookie': '',
            'Host': 'fanyi.qq.com',
            'Origin': 'https://fanyi.qq.com',
            'Referer': 'https://fanyi.qq.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/73.0.3683.86 Safari/537.36', }

        self.fromlang = 'auto'
        self.tolang = 'zh'
        self.sessionUuid = str(int(time.time() * 1000))

        self.fy_guid, self.qtv, self.qtk = get_qtv_qtk()

        self.headers['X-Forwarded-For'] = self.get_ip()
        self.headers['Cookie'] = self.headers['Cookie'].replace(
            '605ead81-f210-47eb-bd80-ac6ae5e7a2d8', self.fy_guid)

        self.headers['Cookie'] = self.headers['Cookie'].replace(
            'ed286a053ae88763', self.qtv)
        self.headers['Cookie'] = self.headers['Cookie'].replace(
            'wfMmjh3k/7Sr2xVNg/LtITgPRlnvGWBzP9a4FN0dn9PE7L5jDYiYJnW03MJLRUGHEFNCRhTfrp/V+wUj0dun1KkKNUUmS86A/wGVf6ydzhwboelTOs0hfHuF0ndtSoX+N3486tUMlm62VU4i856mqw==',
            self.qtk)
    def get_ip(self):
        return ""+str(random.randint(20,190))+"."+\
               str(random.randint(20,190))+"."+\
               str(random.randint(20,190))+"."+\
               str(random.randint(20,190))

    def get_trans_result(self, text):


        data = {
                'source': self.fromlang,
                'target': self.tolang,
                'sourceText': text,
                'qtv': self.qtv,
                'qtk': self.qtk,
                'sessionUuid': self.sessionUuid
               }

        self.headers['X-Forwarded-For'] = self.get_ip()
        trans_result = getHtml(self.api_url, self.headers, data)
        return trans_result


if __name__ == '__main__':
    Tencent = TencentTrans()
    text = 'love'
    print(Tencent.get_trans_result(text))