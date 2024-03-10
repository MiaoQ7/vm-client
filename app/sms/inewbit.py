import requests
from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger
from app.state.loop import bb,tt,fs

headers={
  'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'
}

class InewbitClient(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.data = params
        # self.server_url = params.get("serverUrl", bb.config.taskServerURL)
        self.server_url = bb.config.taskServerURL
        # areaName = self.data.get("area").get("name")
        # self.country = areaCodeToCountry.get(areaName)
        # if self.country is None:
          # raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.country = self.data["area"]["name"]
        self.areaCode = self.data["area"]["code"]
        self.username = params.get("account", "")
        self.password = params.get("password", "")
        self.token = ""
        self.product = params.get("projectId", "")
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "inewbit")
        self.vpsID = vpsID
        self.serverPath = serverPath
        self.orderId = None
        self.urlTokenPayload = None

    def login(self):
      return True

    def getCellNum(self):
        if self.cellNum is None:
            for i in range(10):
                res = self.send(f"/api/phoneCode/getPhone", {
                  "platform": self.platformCode,
                  "areaCode": self.areaCode,
                  "country": self.country,
                })
                data = res.json()
                if data["code"] == 1:
                    self.cellNum = data["data"]["phone"]
                    if data["data"]["virtual"] is True:
                      self.phoneRelease("不支持虚拟号注册")
                      return None
                    self.urlTokenPayload = data["data"]["payload"]
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
        tokenUrl = self.urlTokenPayload["url"].replace("{{token}}", self.urlTokenPayload["token"])

        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = ihttp.get(tokenUrl, headers=headers)
            res.encoding = "utf-8"
            message = res.text
            try:
              message = message.replace('-', '')
              message = message.replace(' ', '')
              matchs = re.search(r"([0-9]{6})", message)
              if matchs is not None:
                self.msg = matchs.group()
                return self.msg
            except Exception as e:
                print(e)
            time.sleep(2)
        return self.msg

    def send(self, path, params={}):
        headers = {
          "Accept": "application/json",
        }
        params = {
          **params,
          "vpsID": tt.get_machine_id(),
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
            result = self.send(f"/api/phoneCode/phoneRelease", {
              "platform": self.platformCode,
              "result": "success" if status == "success" else "failed",
              "msg": status,
              "phone": self.cellNum,
            })
            if result.status_code == 200:
                self.cellNum = None
                return
            time.sleep(3)

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease(status)
        elif status == "failed":
            self.phoneRelease("业务注册失败")
        else:
            self.phoneRelease("业务注册失败")
        self.cellNum = None
