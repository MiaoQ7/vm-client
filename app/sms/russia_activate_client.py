from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

areaCodeToCountry = {
    "Russia": "0",
    "Ukraine": "1",
    "Kazakhstan": "2",
    "China": "3",
    "Kyrgyzstan": "11",
    "United States": "12",
    "Poland": "15",
    "Nigeria": "19",
    "Macau (China)": "20",
    "South Africa": "31",
    "Romania": "32",
    "Estonia": "34",
    "Azerbaijan": "35",
    "United Kingdom": "16",
    "Canada": "36",
    "Malaysia": "7",
    "Germany": "43",
    "Spain": "56",
    "Indonesia": "6",
    "Vietnam": "10",
    "Thailand": "52",
    "India": "22",
    "Brazil": "73",
    "Turkey": "62",
    "Argentina": "39",
    "Pakistan": "66",
}
class RussiaActivateClient(ISMS):

    def __init__(self, params, vpsID, serverPath):
        global areaCodeToCountry
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.service = params.get("projectId", "ig")
        self.data = params
        self.server_url = params.get("serverUrl", "http://sms-activate.ru/stubs/handler_api.php")
        areaName = self.data.get("area").get("name")
        self.country = areaCodeToCountry.get(areaName)
        if self.country is None:
          raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.token = params.get("account", "84f2762B00f7332070d1303cd53f4f31")
        self.tzid = "295509599"
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "sms-activate")
        self.vpsID = vpsID
        self.serverPath = serverPath

    def login(self):
        params = {
            "action": "getBalance"
        }
        res = self.send(params)
        if res.status_code == 200 and res.text is not None:
            split = res.text.split(":")
        if split is not None and len(split) == 2 and "ACCESS_BALANCE" == split[0]:
            self.hasYuE = float(split[1]) >= 8
        return self.hasYuE

    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "action": "getNumber",
                "country": self.country,
                "service": self.service
            }
            for i in range(10):
                res = self.send(params)
                if res.status_code == 200 and res.text is not None:
                    split = res.text.split(":")
                    if split is not None and len(split) == 3 and "ACCESS_NUMBER" == split[0]:
                        self.tzid = split[1]
                        self.cellNum = split[2]
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
        params = {
            "action": "setStatus",
            "id": self.tzid,
            "status": 1
        }
        res = self.send(params)
        if res.status_code == 200 and res.text is not None:
            if res.text == "BAD_STATUS":
                params["status"] = 3
                res = self.send(params)
        return "success"

    def querySMS(self):
        # if self.msg is not None:
        self.setStatus()
        self.msg = None
        params = {
            "action": "getStatus",
            "id": self.tzid
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = self.send(params)
            if res.status_code == 200 and res.text is not None:
                try:
                    if res.text == "STATUS_WAIT_CODE":
                        pass
                    elif res.text == "STATUS_WAIT_RESEND":
                        time.sleep(3)
                    else:
                        split = res.text.split(":")
                        if split is not None and len(split) == 2:
                            if "STATUS_OK" == split[0]:
                                self.msg = self.parseDYSMSCode(split[1])
                                return self.msg
                except Exception as e:
                    print(e)
            time.sleep(2)
        return self.msg

    def send(self, params):
        params["api_key"] = self.token
        for i in range(3):
            result = ihttp.get(self.server_url, params=params)
            result.encoding = "utf-8"
            logger.info(result.text)
            if result.status_code == 200:
                return result
            time.sleep(3)

    def phoneRelease(self, status):
        params = {
            "action": "setStatus",
            "id": self.tzid,
            "status": status
        }
        for i in range(3):
            result = self.send(params)
            if result.status_code == 200:
                self.cellNum = None
                return
            time.sleep(3)

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
