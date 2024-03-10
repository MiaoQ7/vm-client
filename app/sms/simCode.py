from .isms import ISMS
from app.libs import ihttp
import time
import json
from loguru import logger


class SimCode(ISMS):
    def __init__(self, params, vpsID, serverPath):
        super(SimCode, self).__init__(params, vpsID, serverPath)
        self.identifyKey = params.get("account", "a0390e63")
        self.server_url = params.get("serverUrl", "https://chothuesimcode.com/api")
        self.hasYuE = False
        self.applicationId = (int)(params.get("projectId", 1011))
        self.cellNum = None
        self.OPTId = None

    def login(self):
        params = {
            "act": "account",
        }
        res = self.send(params)
        if res.text is not None:
            res = json.loads(res.text)
        if res.get("Result") is not None and res.get("Result").get("Balance") is not None:
            self.hasYuE = res.get("Result").get("Balance") > 0
        return self.hasYuE

    def getCellNumSend(self):
        if self.applicationId is not None:
            params = {
                "act": "number",
                "appId": self.applicationId
            }
            res = self.send(params)
            res = json.loads(res.text)
            if res.get("Result") is not None:
                self.cellNum = "+84"+res.get("Result").get("Number")
                self.OPTId = res.get("Result").get("Id")
        else:
            logger.info("没有zalo对应app id")

    def getCellNum(self):
        if self.cellNum is None:
            self.loopGetCellNum()
        return self.cellNum

    def querySMS(self):
        params = {
            "act": "code",
            "id": self.OPTId,
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send(params)
            data = json.loads(data.text)
            if data is not None and data['ResponseCode'] == 0:
                self.msg = data['Result']['Code']
                break
            time.sleep(3)
        return self.msg

    def phoneRelease(self, status):
        params = {
            "act": "expired",
            "id": self.OPTId,
        }
        for i in range(3):
            data = self.send(params)
            data = json.loads(data.text)
            if data.get("ResponseCode") is not None:
                break
        self.cellNum = None
        self.OPTId = None

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease()
        # elif status == "failed":
        #     action = 'addBlack'
        #     params = {
        #         "pn": self.cellNum,
        #     }
        #     for i in range(3):
        #         if self.send(action, params) is not None: break
        else:
            self.phoneRelease()
        self.cellNum = None
        self.orderId = None

    def send(self, params):
        params["apik"] = self.identifyKey
        for i in range(3):
            result = ihttp.get(self.server_url, params=params)
            result.encoding = "utf-8"
            if result.status_code == 200:
                return result
            time.sleep(3)