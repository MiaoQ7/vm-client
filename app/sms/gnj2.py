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
class Gnj2Client(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.data = params
        self.server_url = params.get("serverUrl", "http://dmd.constancesky.com/pickCode-api/push")
        # areaName = self.data.get("area").get("name")
        # self.country = areaCodeToCountry.get(areaName)
        # if self.country is None:
          # raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.country = self.data["area"]["abbr"]
        self.key = params.get("account", "a3546af3538a20878e5b7be5867e7720")
        self.token = ""
        self.product = params.get("projectId", "10007")
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "gnj2")
        self.vpsID = vpsID
        self.serverPath = serverPath
        self.orderId = None

    def login(self):
        res = self.send("/ticket", {"key": self.key})
        data = res.json()
        if data["code"] == "200":
          self.token = data["data"]["token"]
          return True
        return False

    def getCellNum(self):
        if self.cellNum is None:
            for i in range(10):
                res = self.send(f"/buyCandy", {
                  "businessCode": self.product,
                  "quantity": 1,
                  "country": self.country,
                  "effectiveTime": "10",
                })
                data = res.json()
                if data["code"] == "200":
                    phone_item = data["data"]["phoneNumber"][0]
                    self.orderId = phone_item["serialNumber"]
                    self.cellNum = phone_item["number"]
                    # errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                    errormessage = self.checkPhone(self.cellNum[len(self.data["area"]["code"]) + 1:], self.data["area"]["code"])
                    if errormessage is None:
                        break
                    else:
                        self.phoneRelease("A", "该手机号已经使用过")
                time.sleep(3)
            self.logPhone(self.cellNum)
        return self.cellNum
       

    def querySMS(self):
        self.msg = None
       
        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = self.send(f"/sweetWrapper", {"serialNumber": self.orderId})
            data = res.json()
            if data["code"] == "200":
                try:
                  if "verificationCode" in data["data"]:
                    verificationCode = data["data"]["verificationCode"]
                    if len(verificationCode) > 0:
                      matchs = re.search("(\d{3}-\d{3})", verificationCode[0]["vc"])
                      if matchs is not None:
                        code = matchs.group()
                        self.msg = code.replace("-", "")
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
          "token": self.token,
        }
        for i in range(3):
            result = ihttp.post(self.server_url + path, params=params, headers=headers)
            result.encoding = "utf-8"
            # logger.info(f"status: {result.status_code}, content: {result.text}")
            if result.status_code == 200:
                return result
            time.sleep(3)

    def phoneRelease(self, status, description="phoneRelease"):
        for i in range(3):
            result = self.send(f"/redemption", {"serialNumber": self.orderId, "feedbackType": status, "description": description})
            if result.status_code == 200:
                self.cellNum = None
                return
            time.sleep(3)

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease("A", "业务注册完成")
        elif status == "failed":
            self.phoneRelease("B", "业务注册失败")
        else:
            self.phoneRelease("B", "业务注册失败")
        self.cellNum = None
