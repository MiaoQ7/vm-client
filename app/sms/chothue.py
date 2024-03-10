import requests
from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

defaultServerUrl = "https://chothuesimcode.com/api"

resKey = "ResponseCode"
resCode = 0


class Chothue(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.data = params
        self.server_url = params.get("serverUrl", defaultServerUrl)
        # areaName = self.data.get("area").get("name")
        # self.country = areaCodeToCountry.get(areaName)
        # if self.country is None:
          # raise Exception(f"卡商没有配置对应的国家{areaName}")
        # self.country = self.data["area"]["code"]
        # self.username = params.get("account", "hyun855")
        self.password = params.get("password", "a0390e63")
        self.projectId = params.get("projectId", "1024")
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "chothue")
        self.vpsID = vpsID
        self.serverPath = serverPath
        self.orderId = None

    def login(self):
        res = self.send({
          "act": "account",
        })
        data = res.json()
        if data[resKey] == resCode and data["Result"]["Balance"] > 0:
           return True
        return False

    def getCellNum(self):
        if self.cellNum is None:
            for i in range(10):
                res = self.send({
                  "act": "number",
                  "appId": self.projectId,
                  # "carrier": "",
                  # "prefix": self.country,
                  # "mobile": "number"
                })
                '''
                {
                    "ResponseCode": 0,
                    "Msg": "OK",
                    "Result": {
                        "Id": 122976070,
                        "Number": "843044146",
                        "App": "WhatsApp",
                        "Cost": 0.3,
                        "Balance": 225.85
                    }
                }
                '''
                data = res.json()
                if data[resKey] == resCode:
                  result = data["Result"]
                  self.orderId = result["Id"]
                  self.cellNum = result["Number"]
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
        return "+84" + self.cellNum


    def querySMS(self):
        self.msg = None

        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = self.send({
              "act": "code",
              "id": self.orderId,
            })
            '''
            {
                "ResponseCode": 0,
                "Msg": "OK",
                "Result": {
                    "SMS": "Your Zalo code is 6544",
                    "Code": "6544",
                    "Cost": 1000,
                    "IsCall": false,
                    "CallFile": null
                }
            }
            '''
            data = res.json()
            if data[resKey] == resCode:
              try:
                result = data["Result"]
                self.msg = result["Code"]
                return self.msg
              except Exception as e:
                print(e)
            time.sleep(5)
        return self.msg

    def send(self, params={}):
        headers = {
        }
        params = {
          **params,
          "apik": self.password,
        }
        for i in range(3):
          result = ihttp.get(self.server_url, params=params, headers=headers)
          result.encoding = "utf-8"
          logger.info(f"status: {result.status_code}, content: {result.text}")
          if result.status_code == 200:
            return result
          time.sleep(3)

    def phoneRelease(self, status):
        for i in range(3):
            result = self.send({
              "act": "expired",
              "id": self.orderId,
            })
            data = res.json()
            if data[resKey] == resCode:
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
