from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

# API  https://sms-code.ru/cabinet/api
class LSJClient(ISMS):

    def __init__(self, params, vpsID, serverPath):
        if params is None:
            params = {
                "area": {
                    "code": "7",
                    "name": "Russia",
                    "abbr": "RU"
                }
            }
        self.service = params.get("projectId", "14")
        self.data = params
        self.server_url = params.get("serverUrl", "http://api.kzvepo.com:2086/registerApi")
        self.server_url = re.sub(r'/+$', "", self.server_url)       #去除最后面的/
        abbr = self.data.get("area").get("abbr")
        self.country = abbr.upper()
        if self.country is None:
            areaName = self.data.get("area").get("name")
            raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.uid = params.get("account", "1659289184")
        self.sign = params.get("password", "1b60f4a31ca4d002a8b753f3f65c3e6e")

        self.tzid = None
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "lsj")
        self.vpsID = vpsID
        self.serverPath = serverPath

    def send(self, action, params):
        params["uid"] = self.uid
        params['sign'] = self.sign
        res = self.loopSendGet(f'{self.server_url}/{action}', params)
        if res.ok:
            try:
                return res.json()
            except Exception:
                pass
        return None

    def isOk(self, data):
        return data.get('code') == 0

    '''
{
    "msg": "success",
    "code": 0,
    "data": {
        "score": [
            {
                "gold": 20,
                "pid": 14
            }
        ],
        "createTime": "2022-07-30 21:53:04",
        "userName": "pp22-ws001"
    }
}
    '''
    def login(self):
        params = {
        }
        data = self.send("getUserInfo", params)
        if self.isOk(data):
            self.hasYuE = True
        return self.hasYuE

    '''
    http://api.kzvepo.com:2086/registerApi/getMobile?uid=${uid}&size=1&pid=14&sign=${sign}&cuy=IN
{
    "msg": "success",
    "code": 0,
    "data": [
        917877813313
    ],
    "size": 1,
    "orderId": "1003708177951432704"
}
    '''
    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "size": 1,
                "pid": self.service,
                "cuy": self.country
            }
            for i in range(10):
                data = self.send("getMobile", params)
                if self.isOk(data):
                    self.tzid = data['orderId']
                    self.cellNum = str(data['data'][0])
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
    http://api.kzvepo.com:2086/registerApi/getMsg?uid=${uid}&orderId=${orderId}&sign=${sign}
{
	"data":[            成功才有data字段
		{
			"txt":"మీ WhatsApp కోడ్‌ను ఎవరితోనూ షేర్ చేయవద్దు: 835-834\n\n",
			"country":"IN",
			"code":"835-834",
			"hm":"919242856958",
			"cty":1,
			"time":"1659349762254"
		}
	],
	"error":0
}
    '''
    def querySMS(self):
        # if self.msg is not None:
        self.msg = None
        params = {
            "orderId": self.tzid
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60 * 3
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send("getMsg", params)

            if data.get("data") != None:
                self.msg = self.parseDYSMSCode(str(data['data'][0]['code']).replace('-', ''))
                return self.msg
            time.sleep(5)
        return self.msg

    '''
    http://api.kzvepo.com:2086/registerApi/callBlack?uid=1659189184&sign=${sign}&tid=${tid}&number=917017047167&status=4
{
    "msg": "success",
    "code": 0,
    "data": 1
}
    '''
    def phoneRelease(self, status):
        params = {
            # "pid": self.service,
            "number": self.cellNum,
            "tid": self.tzid,
            "status": status,
        }
        result = self.send("callBlack", params)
        self.cellNum = None

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease(4)
        # elif status == "failed":
        else:
            self.phoneRelease(3)
        # self.phoneRelease(8)
        self.cellNum = None
