#!/usr/bin/env python
# coding: utf-8
import random
import re
import time
import requests
from traceback import print_exc
import json

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
    
    api_url = 'https://fanyi.qq.com/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Chrome/73.0.3683.86 Safari/537.36', }

    res = requests.get(api_url, headers=headers)
    fy_guid = res.cookies.get('fy_guid')

    data = res.text
    reg = re.compile(r'reauthuri = "(.*?)"')
    uri = reg.search(data).group(1)
    api_url = 'https://fanyi.qq.com/api/' + uri

    res = requests.post(api_url, None, headers=headers)

    json_res = json.loads(res.text)
    qtv = json_res["qtv"]
    qtk = json_res["qtk"]

    return fy_guid, qtv, qtk


def getHtml(url,headers,data):

    try:
        html= requests.post(url=url,data= data,headers=headers)
        datas = html.json()['translate']['records']
        
        if html!=None and datas != None :
            trans_result = ''.join([data['targetText'] for data in datas])

    except Exception:
        # print_exc()
        trans_result = '1331'

    return trans_result


class TencentTrans(object):
    
    def __init__(self):
        
        self.api_url = 'https://fanyi.qq.com/api/translate'
        self.headers = {
            'Cookie': '',
            'Host': 'fanyi.qq.com',
            'Origin': 'https://fanyi.qq.com',
            'Referer': 'https://fanyi.qq.com/',
            'User-Agent': 'Mozilla/4.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
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

        trans_result = getHtml(self.api_url, self.headers, data)
        while trans_result == "1331" or not len(trans_result):
            self.__init__()
            trans_result = getHtml(self.api_url, self.headers, data)
        return trans_result


if __name__ == '__main__':
    Tencent = TencentTrans()
    text = 'love'
    print(Tencent.get_trans_result(text))