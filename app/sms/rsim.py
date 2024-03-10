import requests
from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger


'''
200 成功
204 当前业务繁忙，没有手机号可供使用，请稍后重试
205 业务查询为空
206 账号余额不足
207 验证码超时
208 账号禁用
209 秘钥错误
210 Token 错误
213 当前手机号正在执行其他业务，请稍后重试
214 拉取手机号次数不足，请联系平台管理人员
216 手机号已经下线
219 无权限使用该国家手机号
220 垄断时间这个参数错误
'''
class RSimClient(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.data = params
        self.server_url = params.get("serverUrl", "http://154.38.103.254:27123")
        # areaName = self.data.get("area").get("name")
        # self.country = areaCodeToCountry.get(areaName)
        # if self.country is None:
          # raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.country = self.data["area"]["abbr"]
        self.username = params.get("account", "agt1949")
        self.password = params.get("password", "laskdjfh;tihf")
        self.token = "46197101b2feb434"
        self.product = params.get("projectId", "1001")
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "rsim")
        self.vpsID = vpsID
        self.serverPath = serverPath
        self.orderId = None

    def login(self):
        # res = self.send("/login.php", {"username": self.username, "password": self.password})
        # data = res.json()
        # if data["result"] == "success":
        #   self.token = data["token"]
        #   self.hasYuE = float(data["integral"]) > 0
        #   return self.hasYuE
        # return self.hasYuE
        return True

    def getCellNum(self):
        if self.cellNum is None:
            for i in range(10):
                res = self.send(f"/getphonumber/{self.token}/{self.product}/1")
                data = res.json()
                if data["code"] == 200:
                    self.orderId = data["data"][0]
                    self.cellNum = "9" + data["data"][0]
                    # errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                    errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                    if errormessage is None:
                        break
                    else:
                        self.phoneRelease("该手机号已经使用过")
                time.sleep(3)
            if self.cellNum is None:
              return None
            self.logPhone(self.cellNum)
        return "+" + self.data["area"]["code"] + self.cellNum
       

    def querySMS(self):
        self.msg = None
       
        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = self.send(f"/getsms/{self.token}/{self.orderId}/{self.product}")
            data = res.json()
            if data["code"] == 200:
              try:
                matchs = re.search("([0-9]{4,6})", data["data"]["msg"])
                if matchs is not None:
                  self.msg = matchs.group()
                  return self.msg
              except Exception as e:
                  print(e)
            time.sleep(5)
        return self.msg

    def send(self, path, params={}):
        headers = {
          "Accept": "application/json",
        }
        params = {
          **params,
        }
        for i in range(3):
            result = ihttp.get(self.server_url + path, params=params, headers=headers)
            result.encoding = "utf-8"
            # logger.info(f"status: {result.status_code}, content: {result.text}")
            if result.status_code == 200:
                return result
            time.sleep(3)

    def phoneRelease(self, status):
        for i in range(3):
            result = self.send(f"/addblack/{self.token}/{self.orderId}/{self.product}")
            if result.status_code == 200:
                self.cellNum = None
                return
            time.sleep(3)

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease("业务注册完成")
        elif status == "failed":
            self.phoneRelease("业务注册失败")
        else:
            self.phoneRelease("业务注册失败")
        self.cellNum = None
