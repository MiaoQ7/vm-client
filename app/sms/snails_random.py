import hashlib
import json

from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

# https://www.firefox.fun/Ashx/Public.ashx
# form-data
# act:PagCountry

# API  http://www.firefox.fun/apihelp.aspx
class SnailsRandom(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
            params = {
                "area": {
                    "code": "7",
                    "name": "Russia",
                    "abbr": "RU"
                }
            }
        super(SnailsRandom, self).__init__(params, vpsID, serverPath)
        if not self.server_url: self.server_url = "http://8.219.111.2:9003/api/"
        self.areas = {}
        with open('area.json', 'r', encoding='utf8')as fp:
            data = json.load(fp)
            for item in data:
                self.areas[item["abbr"]] = item

    def send(self, action, params):
        for i in range(3):
            params['channel'] = self.account
            params['t'] = str(int(time.time() * 1000 + time.time_ns() // 1000000))
            sign = self.createSign(params, self.password)
            params["sign"] = sign
            res = ihttp.post(f'{self.server_url}{action}', data=params, headers={'Content-Type': 'application/x'
                                                                                                    '-www-form'
                                                                                                    '-urlencoded'})
            logger.info(res.text)
            if res.ok:
                try:
                    return res.json()
                except Exception:
                    pass
        return None

    def isOk(self, data):
        return data and data[0] == "1"

    '''
    http://www.firefox.fun/yhapi.ashx?act=login&ApiName=12348&PassWord=1231
    1|token值
    '''

    def login(self):
        return True
        # params = {
        #     "ApiName": self.account,
        #     "PassWord": self.password,
        # }
        # data = self.send("login", params)
        # if self.isOk(data):
        #     self.token = data[1]
        #     self.hasYuE = True
        # return self.hasYuE

    def createSign(self, data, secret):
        newKeys = list(data.keys())
        newKeys.sort()
        signStr = ""
        for i, item in enumerate(newKeys):
            signStr += newKeys[i] + "=" + data[newKeys[i]]
        signStr += secret
        hash_md5 = hashlib.md5()
        hash_md5.update(signStr.encode())
        encrypted_data = hash_md5.hexdigest()
        return encrypted_data

    '''
    http://www.firefox.fun/yhapi.ashx?act=getPhone&token=token&iid=1001&did=&country=&operator=&provi=&city=&seq=0&mobile=
    1|pkey|提取时间|国家代码|运营商|归属地|端口号|手机号
    '''
    def getCellNum(self):
        if self.cellNum is None:
            for i in range(10):
                params = {
                    "pid": self.service,
                }
                data = self.send("order", params)
                if data['code'] == 0:
                    if self.areas[data['country']] is not None:
                        self.data["area"] = self.areas[data['country']]
                        self.area = self.areas[data['country']]
                        self.taskid = data['taskid']
                        self.cellNum = data['phone'][1:]
                        errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                        if errormessage is None:
                            break
                        else:
                            self.phoneRelease("该手机号已经使用过")
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
    http://www.firefox.fun/yhapi.ashx?act=getPhoneCode&token=${token}&pkey=${pkey}
    1|验证码数字|完整短信内容
    '''

    def querySMS(self):
        # if self.msg is not None:
        self.msg = None
        timeout = int(round(time.time() * 1000)) + 1000 * 60 * 3
        for i in range(10):
            if int(round(time.time() * 1000)) > timeout:
                break
            params = {
                "taskid": self.taskid,
            }
            data = self.send("code", params)
            if data['code'] == 0:
                self.msg = self.parseDYSMSCode(data['vcode'])
                return self.msg
            time.sleep(5)
        return self.msg

    '''
    http://www.firefox.fun/yhapi.ashx?act=setRel&token=${token}&pkey=${pkey}
    1|
    '''

    # 如果对接卡商开通了apiReturn反馈接口,需要通过反馈接口反馈是否注册成功,以保证收到短信后如果注册失败不扣费
    # (固定值 0：成功，-1：失败，-2：验证码超时，-3：号码已注册)，其他信息请直接输入
    def apiReturn(self, remark):
        pass

    def phoneRelease(self, status):
        params = {
            "phone": self.cellNum,
        }
        result = self.send("releasePhone", params)

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.apiReturn(0)     #如不反馈,超时后如收到验证码就扣费
            pass
            # self.phoneRelease(6)
        elif status == "failed":
            self.apiReturn(msg)
            self.phoneRelease(8)
        else:
            self.apiReturn(msg)
            self.phoneRelease(8)
        self.cellNum = None


# API  http://www.firefox.fun/apihelp.aspx
class SnailsRandom2(SnailsRandom):
    # 如果对接卡商开通了apiReturn反馈接口,需要通过反馈接口反馈是否注册成功,以保证收到短信后如果注册失败不扣费
    # (固定值 0：成功，-1：失败，-2：验证码超时，-3：号码已注册)，其他信息请直接输入
    def apiReturn(self, remark):
        params = {
            "pkey": self.tzid,
            "remark": remark,
        }
        result = self.send("apiReturn", params)
