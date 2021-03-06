import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
try:
    cred = credential.Credential("AKIDjDTO9fS3oeJkumNQnw5CySiklW5VLLNj", "HSNJIGyQcY8Tm2XnoZtZ1E9tOtCZcZXH")
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tmt.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

except TencentCloudSDKException as err:
    print(err)


import json
import _thread
# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
# import selenium.common.exceptions as ee
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
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

# ???????????????????????????
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
                #???????????????????????????
                locks[retPool["pid"]]= 1
                nowstr, index = getOneQueue(retPool["pid"])
                locks[retPool["pid"]] = 0
                if index != -1:
                    findRetPool = retPool
                    break

        if findRetPool:
            aa = nowstr.replace('\n', ' ')

            if aa.count(" ") > 2:

                # 1.??????api
                ret = driver.get_trans_result(aa)

                print(ret)
                # ????????????
                # eache.set(aa.lower(), ret)
            else:
                ret = ""
            # ??????????????????retPool,index???
            findRetPool[str(index)]["temp"] = ret
            findRetPool[str(index)]["state"] = 1
            findRetPool["num"] += 1

def buildTranslatorPool():
    # ??????????????????
    try:
        N = 0
        for i in range(N):
            driver = Tencent.TencentTrans()

            _thread.start_new_thread(translator, ("Thread-"+str(i), driver))
            print("build " + str(i) + " finished!")
        print("all build "+ str(N) + " finished!")
    except:
        print("Error: ??????????????????")

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
        # ????????????????????????,????????????????????????target???
        locks[retPool["pid"]] = 1
        for i in range(retPool["num"]):
            ret = retPool[str(i)]["temp"]
            count = {"confidence": 0.8, "count": 0, "rc": 0, "sentence_id": 0, "target": ret, "trans_type": type}
            targets.append(count)
            # ??????retPool
            retPool["num"] = 0
        return True
    return False

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class PostHandler(BaseHTTPRequestHandler):
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
        req_datas = self.rfile.read(int(self.headers['content-length']))  # ???????????????!
        info = req_datas.decode()
        jinfo = json.loads(info)
        type = jinfo['trans_type']
        pid = jinfo['page_id']
        queue = jinfo["source"]
        url = jinfo["url"]
        isyoutubetitle = False
        if url.find("youtube") != -1 and len(queue) == 2:
            isyoutubetitle = True
        data = {
            "confidence": 0.8,
            "page_id": pid,
            "target": [],
            "rc":0,
        }
        #????????????
        # sessionIdStr = str(time.time())
        for i in range(len(queue)):
            aa = queue[i]
            aa = aa.replace('\n', ' ')
            # aa = aa.lower()
            count = {"confidence": 0.8, "count": 0, "rc": 0, "sentence_id": 0, "target": "", "trans_type": type}
            ret = ""

            if isyoutubetitle and i == 0:
                ret = ""
            elif aa.count(" ") < 7 and eache.get(aa) and type[0:2] == "en":
                ret = str(eache.get(aa), encoding="utf-8")
            else:
                if isyoutubetitle and i == 1:
                    aa = queue[0] + queue[1]
                req = models.TextTranslateRequest()
                params = {
                    "SourceText": aa,
                    "Source": "en",
                    "Target": "zh",
                    "ProjectId": 0
                }
                req.from_json_string(json.dumps(params))
                try:
                    ret = client.TextTranslate(req).TargetText
                except TencentCloudSDKException as err:
                    print(err)
                gangi = ret.find("/")
                if aa.count(" ") < 2 and gangi != -1:
                    ret = ret[0:gangi-1]
                print(ret)
                if aa.count(" ") < 7 and type[0:2] == "en":
                    eache.set(aa, ret)
            ret = '''
            '''+ret
            count = {"confidence": 0.8, "count": 0, "rc": 0, "sentence_id": 0, "target": ret, "trans_type": type}
            data["target"].append(count)

        # locks[sessionIdStr] = 1
        # fanyi(retPools, sessionIdStr, queue)
        # locks[sessionIdStr] = 0

        # while True:
        #     finished = getRet(retPools[sessionIdStr], data["target"], type)
        #     if finished:
        #         break

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
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, "
                                                         "X-Authorization, Referrer")
        self.send_header("Access-Control-Allow-Credentials", 'true')
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
    _thread.start_new_thread(buildTranslatorPool,())
    start_server()
