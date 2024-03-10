from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

class WOODClient(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
            params = {
                "area": {
                    "code": "63",
                    "name": "Philippines",
                    "abbr": "PH"
                }
            }
        super(WOODClient, self).__init__(params, vpsID, serverPath)
        if not self.server_url: self.server_url = "http://8.218.59.226/WOODServer/api/Function"

    def send(self, action, params):
        res = self.loopSendGet(f"{self.server_url}/{action}", params)
        if res.ok:
            try:
                return res.json()
            except Exception:
                pass
        return None

    def isOk(self, data):
        return data and data['status'] == "0"

    '''
    http://8.218.59.226/WOODServer/api/Function/AccountGetAmount?account=账号&password=密码
    成功返回：{"status":"0","msg":1000}
    失败返回：{"status":"1"，"msg","错误信息"}
    '''
    def login(self):
        params = {
            "account": self.account,
            "password": self.password,
        }
        data = self.send("AccountGetAmount", params)
        if self.isOk(data):
            self.hasYuE = True
        return self.hasYuE

    '''
    http://8.218.59.226/WOODServer/api/Function/PhoneNumberByProject?account=账号&pwd=密码&project=项目编号
    成功返回：{"status":"0","count":"1","phone":[12347375430],"number":"12347375430"，"phonecode":"2234678"}
    phonecode：手机号唯一标识
    number：手机号
    失败返回：{"status":"1"，"msg","错误信息"}
    '''
    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "account": self.account,
                "pwd": self.password,
                "project": self.service
            }
            for i in range(10):
                data = self.send("PhoneNumberByProject", params)
                if self.isOk(data):
                    self.tzid = data["phonecode"]
                    self.cellNum = data["number"]
                    errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                    if errormessage is None:
                        break
                    else:
                        self.phoneRelease(8)

                time.sleep(3)

            if self.cellNum is None:
                return None
            else:
                self.logPhone(self.cellNum)

        if self.cellNum is not None and self.data is not None and self.data.get("area") is not None and self.data.get("area").get("code") is not None:
            code = self.data.get("area").get("code")  # 去掉号码中的区号
            matches = re.match(code, self.cellNum)
            if matches is None:
                # return self.cellNum[len(code): len(self.cellNum)]
                return "+" + code + self.cellNum
        return "+" + self.cellNum

    '''
    http://8.218.59.226/WOODServer/api/Function/VerifyCode?account=账号&pwd=密码&phonecode=2234678
    phonecode：手机号唯一标识
    成功返回：{"status":"0"，"msg","验证码"}
    失败返回：{"status":"1"，"msg","错误信息"}
    '''
    def querySMS(self):
        # if self.msg is not None:
        self.msg = None
        params = {
            "account": self.account,
            "pwd": self.password,
            "phonecode": self.tzid
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60 * 3
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send("VerifyCode", params)
            if self.isOk(data):
                self.msg = self.parseDYSMSCode(data["msg"])
                return self.msg
            time.sleep(5)
        return self.msg

    '''
    http://8.218.59.226/WOODServer/api/Function/Black?phonecode=2234678&reason=原因
    phonecode：手机号唯一标识
    成功返回：{"status":"0"，"msg","成功信息"}
    失败返回：{"status":"1"，"msg","错误信息"}
    '''
    def phoneRelease(self, status):
        params = {
            "phonecode": self.tzid,
        }
        result = self.send("Release", params)
        self.cellNum = None

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            pass
            # self.phoneRelease(6)
        elif status == "failed":
            self.send("Release", {
                "phonecode": self.tzid,
                "reason": msg,
            })
        else:
            self.phoneRelease(8)
        self.cellNum = None
