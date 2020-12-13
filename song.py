import json
import _thread
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions as ee
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import redis
import re
# taskkill /F /IM "firefox.exe"
# C:\Users\Administrator\AppData\Local\Programs\Python\Python37\python.exe C:/Users/Administrator/PycharmProjects/tenTranslate/song.py
locks = {
}
retPools = {}
eache = redis.StrictRedis(host='localhost', port=6379, db=0)

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
            # 开始翻译
            try:
                # stopword = ":q"
                # file_content = ""
                # print("请输入内容【单独输入‘:q‘保存退出】：")
                # for line in iter(input, stopword):
                #     file_content = file_content + line + "\n"
                aa = nowstr.replace('\n', ' ')

                # 使用缓存
                if aa.count(" ") < 10 and eache.get(aa.lower()):
                    # 使用缓存
                    ret = eache.get(aa.lower())

                elif aa.count(" ") > -1:
                    input1 = driver.find_element_by_class_name("textinput")

                    input1.send_keys(aa)
                    input1.send_keys('\n')
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "text-dst")))
                    input2 = driver.find_element_by_class_name("textpanel-target-textblock")
                    ret = str(input2.text)
                    findRet = ret.find('/')
                    if findRet != -1 and aa.count(" ") == 0:
                        ret = ret[0:findRet]
                    # ret = re.sub("\n", "", ret)
                    print(ret)
                    input3 = driver.find_element_by_class_name("tool-close")
                    input3.click()

                    # 保存缓存
                    eache.set(aa.lower(), ret)
            except(
            ee.NoSuchElementException, ee.InvalidSessionIdException, ee.TimeoutException, ee.StaleElementReferenceException,
            ee.ElementNotInteractableException):
                driver.close()
                findRetPool[str(index)]["state"] = 0
                break

            # 将结果保存在retPool,index中
            findRetPool[str(index)]["temp"] = ret
            findRetPool[str(index)]["state"] = 1
            findRetPool["num"] += 1

def buildTranslatorPool():
    # 创建两个线程
    try:
        N = 24
        for i in range(N):
            options = Options()
            options.add_argument('-headless')
            driver = Firefox(executable_path='geckodriver', firefox_options=options)
            driver.get("https://fanyi.qq.com/")
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
        req_datas = self.rfile.read(int(self.headers['content-length']))  # 重点在此步!
        info = req_datas.decode()
        jinfo = json.loads(info)
        type = jinfo['trans_type']
        pid = jinfo['page_id']
        queue = jinfo["source"]
        data = {
            "confidence": 0.8,
            "page_id": pid,
            "target": [],
            "rc":0,
        }
        #异步处理
        sessionIdStr = str(time.time())
        locks[sessionIdStr] = 1
        fanyi(retPools, sessionIdStr, queue)
        locks[sessionIdStr] = 0

        while True:
            finished = getRet(retPools[sessionIdStr], data["target"], type)
            if finished:
                break

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
