import time
import re
from app.libs import ihttp
from loguru import logger

class ISMS(object):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
            params = {
                "area": {
                    "code": "7",
                    "name": "Russia"
                }
            }

        self.token = params.get("account")  # 默认用account当token,如果需要通过account和password登陆获取token,则登陆后替换掉token
        self.account = params.get("account")
        self.password = params.get("password")
        self.server_url = params.get("serverUrl")
        self.service = params.get("projectId")
        self.data = params
        self.area = params.get("area")
        self.cellNum = None
        self.orderId = None  # 获取手机号时同时获取到的订单号
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode")
        self.vpsID = vpsID
        self.serverPath = serverPath

    def login(self) -> bool:
        raise NotImplementedError("must be override")

    def getCellNumSend(self):
        raise NotImplementedError("must be override")

    def getCellNum(self):
        raise NotImplementedError("must be override")

    def querySMS(self):
        raise NotImplementedError("must be override")

    def add2BlackList(self, status, msg):
        raise NotImplementedError("must be override")

    def phoneRelease(self, status):
        raise NotImplementedError("must be override")

    def loopSendGet(self, url, params):
        for i in range(3):
            result = ihttp.get(url, params=params)
            logger.info(result.text)
            if result.ok:
                return result
            time.sleep(3)
        return result

    def loopSendPost(self, url, params):
      for i in range(3):
        result = ihttp.post(url, json=params)
        logger.info(result.text)
        if result.ok:
          return result
        time.sleep(3)
      return result

    def loopGetCellNum(self):
        for i in range(10):
            self.getCellNumSend()
            if self.cellNum is not None:
                errmsg = self.checkPhone(self.subAreaCode(self.cellNum), self.area['code'])
                if errmsg is None:
                    break
                else:
                    self.phoneRelease()

        self.logPhone(self.cellNum)

    def subAreaCode(self, phone=None):
        if phone is None:
            phone = self.cellNum
        if phone is not None and self.data is not None and self.data.get("area") is not None and self.data.get("area").get("code") is not None:
            code = self.data.get("area").get("code")  # 去掉号码中的区号
            matches = re.match(re.compile(f'^\+?{code}'), phone)
            if matches is not None:
                return self.cellNum[matches.span()[1]: len(phone)]
        return phone

    def logPhone(self, phone):
        for i in range(5):
            if phone is None:
                return
            phone = self.subAreaCode(phone)
            rsp = ihttp.get(self.serverPath + "/api/phoneCode/logPhone/" + self.vpsID + "/" + phone)
            if rsp.status_code == 200:
                return
            time.sleep(1)

    def addHistoryPhone(self, phone, area, status, platform, code, payload, errorMessage):
        params = {
            "phone": self.subAreaCode(self.cellNum)
        }
        if area.get("code") is not None and area.get("code") != "":
            params["fullPhoneCode"] = area["code"] + self.subAreaCode(phone)

        params["area"] = area
        params["status"] = status
        params["platform"] = platform
        params["code"] = code
        params["payload"] = payload
        params["errorMessage"] = errorMessage
        params["vpsID"] = self.vpsID
        for i in range(5):
            res = ihttp.post(self.serverPath + "/api/phoneCode/addHistoryPhone", json=params)
            if res.status_code == 200:
                return
            time.sleep(1)

    def checkPhone(self, phone, areaCode):
        params = {
            "phone": phone,
            "areaCode": areaCode
        }
        for i in range(5):
            rsp = ihttp.get(self.serverPath + "/api/phoneCode/checkPhone", params=params)
            if rsp.status_code == 200:
                if rsp.json()["code"] == 1:
                    return rsp.json()["errorMessage"]
                else:
                    return None
            time.sleep(1)
        return None

    def parseDYSMSCode(self, captcha):
        matchs = re.search("([0-9]{3,6})", captcha)
        code = None
        if matchs is not None:
            code = matchs.group()
        return code
