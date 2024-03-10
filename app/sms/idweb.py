from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

areaCodeToCountry = {
    "Russia": "RU",
    "Ukraine": "UA",
    "Kazakhstan": "KZ",
    "China": "CN",
    "Kyrgyzstan": "KG",
    "United States": "US",
    "Poland": "PL",
    "Nigeria": "NG",
    "Macau (China)": "MO",
    "South Africa": "ZA",
    "Romania": "RO",
    "Estonia": "EE",
    "Azerbaijan": "AZ",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Malaysia": "MY",
    "Germany": "DE",
    "Spain": "ES",
    "Indonesia": "ID",
    "Vietnam": "VN",
    "Thailand": "TH",
    "India": "IN",
    "Brazil": "BR",
}

class IdWebClient(ISMS):

    def __init__(self, params, vpsID, serverPath):
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.data = params
        self.server_url = params.get("serverUrl", "http://idweb.info")
        areaName = self.data.get("area").get("name")
        self.country = areaCodeToCountry.get(areaName)
        if self.country is None:
          raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.token = params.get("account", "ZXJpYzA4MTAxNjI4NTgyMzQwNjc1Njc5")
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "idweb")
        self.vpsID = vpsID
        self.serverPath = serverPath

    def login(self):
        params = {}
        res = self.send("/do/checkbalance", params)
        if res["code"] == 0:
          balance = res["data"]["balance"].replace("￥", "")
          self.hasYuE = float(balance) > 0
        return self.hasYuE

    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "geo": self.country,
            }
            for i in range(10):
                res = self.send("/do/get", params)
                if res["code"] == 0:
                  data = res["data"]
                  self.cellNum = data["number"]
                  self.msg = data["code"]
                  errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                  if errormessage is None:
                    break
                  else:
                    self.phoneRelease(8)
                time.sleep(3)
            self.logPhone(self.cellNum)
        if self.cellNum is None:
          return None
        if self.cellNum is not None and self.data is not None and self.data.get("area") is not None and self.data.get("area").get("code") is not None:
            code = self.data.get("area").get("code")    #去掉号码中的区号
            matches = re.match(code, self.cellNum)
            if matches is None:
                # return self.cellNum[len(code): len(self.cellNum)]
                return "+" + code + self.cellNum
        return "+" + self.cellNum

    def setStatus(self):
        # params = {
        #     "action": "setStatus",
        #     "id": self.tzid,
        #     "status": 1
        # }
        # res = self.send(params)
        # if res.status_code == 200 and res.text is not None:
        #     if res.text == "BAD_STATUS":
        #         params["status"] = 3
        #         res = self.send(params)
        return "success"

    def querySMS(self):
        # if self.msg is not None:
        # self.setStatus()
        # self.msg = None
        # params = {
        #     "action": "getStatus",
        #     "id": self.tzid
        # }
        # timeout = int(round(time.time() * 1000)) + 1000 * 50
        # for i in range(45):
        #     if int(round(time.time() * 1000)) > timeout:
        #         break
        #     res = self.send(params)
        #     if res.status_code == 200 and res.text is not None:
        #         try:
        #             if res.text == "STATUS_WAIT_CODE":
        #                 pass
        #             elif res.text == "STATUS_WAIT_RESEND":
        #                 time.sleep(3)
        #             else:
        #                 split = res.text.split(":")
        #                 if split is not None and len(split) == 2:
        #                     if "STATUS_OK" == split[0]:
        #                         self.msg = self.parseDYSMSCode(split[1])
        #                         return self.msg
        #         except Exception as e:
        #             print(e)
        #     time.sleep(2)
        return self.msg

    def send(self, path, params):
        params["token"] = self.token
        for _ in range(3):
            result = ihttp.get(self.server_url + path, params=params)
            logger.info(result.text)
            if result.status_code == 200:
                return result.json()
            time.sleep(3)
        return result

    def phoneRelease(self, status):
        # params = {
        #     "action": "setStatus",
        #     "id": self.tzid,
        #     "status": status
        # }
        # for i in range(3):
        #     result = self.send(params)
        #     if result.status_code == 200:
        #         self.cellNum = None
        #         return
        #     time.sleep(3)
        pass

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease(6)
        elif status == "failed":
            self.phoneRelease(8)
        else:
            self.phoneRelease(8)
        self.cellNum = None
