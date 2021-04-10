#!/usr/bin/env python
# coding: utf-8
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import json
import _thread
# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
# import selenium.common.exceptions as ee
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import redis
import re
import Tencent
Tencen = Tencent.TencentTrans()
# taskkill /F /IM "firefox.exe"
# C:\Users\Administrator\AppData\Local\Programs\Python\Python37\python.exe C:/Users/Administrator/PycharmProjects/tenTranslate/song.py
locks = {
}
retPools = {}
eache = redis.StrictRedis(host='localhost', port=6379, db=0)
# class Eache():
#     def __init__(self):
#         self.content = {}
#     def get(self, key):
#         return self.content[key]
#     def set(self, key, value):
#         content[key] = value
# eache = Eache()

# MIME-TYPE
mimedic = [
    ('.html', 'text/html'),
    ('.htm', 'text/html'),
    ('.js', 'application/javascript'),
    ('.css', 'text/css'),
    ('.json', 'application/json'),
    ('.png', 'image/png'),
    ('.jpg', 'image/jpeg'),
    ('.gif', 'image/gif'),
    ('.txt', 'text/plain'),
    ('.avi', 'video/x-msvideo')]

def getOneQueue(pid):
    for i in range(retPools[pid]["targetsnum"]):
        if retPools[pid][str(i)]["state"] == 0:
            retPools[pid][str(i)]["state"] = 2
            return retPools[pid][str(i)]["temp"], i
    return "",-1

# 为线程定义一个函数
def translator(name, driver):
    time.sleep(5)
    ret = ""
    while True:
        lens = len(retPools)
        if lens == 0:
            continue

        findRetPool = None
        nowstr = ""
        index = 0
        for key in list(retPools.keys()):
            retPool = retPools[key]
            if retPool["num"] != retPool["targetsnum"] and locks[retPool["pid"]] == 0:
                #需要取一个进行翻译
                locks[retPool["pid"]]= 1
                nowstr, index = getOneQueue(retPool["pid"])
                locks[retPool["pid"]] = 0
                if index != -1:
                    findRetPool = retPool
                    break

        if findRetPool:
            aa = nowstr.replace('\n', ' ')

            if aa.count(" ") > 2:

                # 1.使用api
                ret = driver.get_trans_result(aa)

                print(ret)
                # 保存缓存
                # eache.set(aa.lower(), ret)
            else:
                ret = ""
            # 将结果保存在retPool,index中
            findRetPool[str(index)]["temp"] = ret
            findRetPool[str(index)]["state"] = 1
            findRetPool["num"] += 1

def buildTranslatorPool():
    # 创建两个线程
    try:
        N = 0
        for i in range(N):
            driver = Tencent.TencentTrans()

            _thread.start_new_thread(translator, ("Thread-"+str(i), driver))
            print("build " + str(i) + " finished!")
        print("all build "+ str(N) + " finished!")
    except:
        print("Error: 无法启动线程")

def fanyi(retPools, pid, queue):
    retPool = {
        "num": 0,
        "targetsnum": 0,
        "pid": pid
    }
    retPools[pid] = retPool

    retPool["num"] = 0
    for i in range(len(queue)):
        retPool[str(i)] = {
            "state": 0,
            "temp": queue[i]
        }
    retPool["targetsnum"] = len(queue)

def getRet(retPool, targets, type):
    if retPool["targetsnum"] == retPool["num"]:
        # 检查是否已经完成,如果完成，就填到target中
        locks[retPool["pid"]] = 1
        for i in range(retPool["num"]):
            ret = retPool[str(i)]["temp"]
            count = {"confidence": 0.8, "count": 0, "rc": 0, "sentence_id": 0, "target": ret, "trans_type": type}
            targets.append(count)
            # 重置retPool
            retPool["num"] = 0
        return True
    return False

driverss = []
driver_lock = threading.Lock()

def getDriver():
    # with driver_lock:
        while len(driverss):
            nextDriver = driverss.pop()
            curTime = time.time()
            if curTime - nextDriver.time < 30:
                return nextDriver
        new_driver = Tencent.TencentTrans()
        return new_driver

def backDriver(driver):
    curTime = time.time()
    if curTime - driver.time < 30:
        driverss.append(driver)


def buildTranslatorPoolNew():
    while True:
        while len(driverss) < 100:
            new_driver = Tencent.TencentTrans()
            backDriver(new_driver)
            # print("翻译者有：！！！！！！！！！！！！！！！！！！！！！！！！！！！" + str(len(driverss)) + "个")


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

badInfos = {}
class PostHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    # GET
    def do_GET(self):
        sendReply = False
        print("get")
        # querypath = urlparse(self.path)
        # filepath, query = querypath.path, querypath.query
        #
        # if filepath.endswith('/'):
        #     filepath += 'index.html'
        # filename, fileext = path.splitext(filepath)
        # for e in mimedic:
        #     if e[0] == fileext:
        #         mimetype = e[1]
        #         sendReply = True
        #
        # if sendReply == True:
        #     try:
        #         with open(path.realpath(curdir + sep + filepath), 'rb') as f:
        #             content = f.read()
        #             self.send_response(200)
        #             self.send_header('Content-type', mimetype)
        #             self.end_headers()
        #             self.wfile.write(content)
        #     except IOError:
        #         self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        req_datas = self.rfile.read(int(self.headers['content-length']))  # 重点在此步!
        info = req_datas.decode()
        jinfo = json.loads(info)
        type = jinfo['trans_type']
        pid = jinfo['page_id']
        queue = jinfo["source"]
        url = jinfo["url"]
        # isyoutubetitle = False
        # if url.find("youtube") != -1 and len(queue) == 2:
        #     isyoutubetitle = True
        data = {
            "confidence": 0.8,
            "page_id": pid,
            "target": [],
            "rc":0,
        }
        #异步处理
        # sessionIdStr = str(time.time())
        for i in range(len(queue)):
            aa = queue[i]
            aa = aa.replace('\n', ' ')
            # aa = aa.lower()
            count = {"confidence": 0.8, "count": 0, "rc": 0, "sentence_id": 0, "target": "", "trans_type": type}
            ret = ""

            # if isyoutubetitle and i == 0:
            #     ret = ""
            if (len(aa) < 25 and type[0:2] == "en" or len(aa) < 10 and type[0:2] == "zh") and eache.get(aa):
                ret = str(eache.get(aa), encoding="utf-8")
            else:
                # if isyoutubetitle and i == 1:
                #     aa = queue[0] + queue[1]
                if len(aa) == 0 or aa == " " or aa == "  " or aa == "   ":
                    ret = aa
                elif badInfos.get(aa):
                    ret = badInfos[aa]
                else:
                    driver = getDriver()
                    ret = driver.get_trans_result(aa)
                    count = 1
                    while count < 5 and (ret == "1331" or ret.count("。") > len(ret)/3 or len(ret) == 0 or ret == " " or ret == "  " or ret == "   "):
                        driver = getDriver()
                        ret = driver.get_trans_result(aa)
                        count += 1

                    if ret == "1331" or ret.count("。") > len(ret) / 3 or len(
                            ret) == 0 or ret == " " or ret == "  " or ret == "   ":
                        if len(aa) < 25:
                            badInfos[aa] = aa
                        ret = aa
                    backDriver(driver)
                    gangi = ret.find("/")
                    if aa.count(" ") < 2 and type[0:2] == "en" and gangi != -1:
                        ret = ret[0:gangi-1]
                    if len(aa) < 25 and type[0:2] == "en" or len(aa) < 10 and type[0:2] == "zh":
                        eache.set(aa, ret)

            a = "原文： " + aa+"\n译文： " + ret+"\n"
            print(a)
            ret = '''
                                            ''' + ret
            count = {"confidence": 0.8, "count": 0, "rc": 0, "sentence_id": 0, "target": ret, "trans_type": type}
            data["target"].append(count)

        # locks[sessionIdStr] = 1
        # fanyi(retPools, sessionIdStr, queue)
        # locks[sessionIdStr] = 0

        # while True:
        #     finished = getRet(retPools[sessionIdStr], data["target"], type)
        #     if finished:
        #         break
        # backDriver(driver)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', "*")
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, "
                                                         "X-Authorization, Referrer")
        self.send_header("Access-Control-Allow-Credentials", 'true')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', "*")
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, X-Authorization, Referrer")
        self.end_headers()

def start_server():
    host = '127.0.0.1'
    port = 9999
    httpd = ThreadingHTTPServer((host, port), PostHandler)
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, ConnectionAbortedError):
        httpd.server_close()

if __name__ == '__main__':
    _thread.start_new_thread(buildTranslatorPoolNew,())
    start_server()
