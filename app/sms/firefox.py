from .isms import ISMS
from app.libs import ihttp
import time
import re

# https://www.firefox.fun/Ashx/Public.ashx
# form-data
# act:PagCountry
areaCodeToCountry = {
    "1": "usa",  # +1/美国/usa
    "7": "rus",  # +7/俄罗斯/russia
    "27": "zaf",  # +27/南非/southafrica
    "44": "eng",  # +44/英格兰/england
    "54": "arg",  # +54/阿根廷/argentina
    "58": "ven",  # +58/委内瑞拉/venezuela
    "60": "mys",  # +60/马来西亚/malaysia
    "62": "idn",  # +62/印度尼西亚/indonesia
    "63": "phl",  # +63/菲律宾/philippines
    "65": "sgp",  # +65/新加坡/singapore
    "66": "tha",  # +66/泰国/thailand
    "84": "vnm",  # +84/越南/vietnam
    "91": "ind",  # +91/印度/india
    "212": "mar",  # +212/摩洛哥/morocco
    "249": "sdn",  # +249/苏丹/sudan
    "261": "mdg",  # +261/马达加斯加/madagascar
    "670": "tls",  # +670/东帝汶/timorleste
    "852": "hkg",  # +852/香港/hongkong
    "855": "khm",  # +855/柬埔寨/cambodia
    "856": "lao",  # +856/老挝/laos
}


# API  http://www.firefox.fun/apihelp.aspx
class FirefoxClient(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
            params = {
                "area": {
                    "code": "7",
                    "name": "Russia",
                    "abbr": "RU"
                }
            }
        super(FirefoxClient, self).__init__(params, vpsID, serverPath)
        if not self.server_url: self.server_url = "http://firefox.fun/yhapi.ashx"
        self.getCountryIDs()
        self.country = areaCodeToCountry.get(self.area['code'])
        if self.country is None:
            areaName = self.area["name"]
            raise Exception(f"卡商没有配置对应的国家{areaName}")

    #动态获取卡商支持地区
    def getCountryIDs(self):
        try:
            url = self.server_url.replace("yhapi", "Ashx/Public")
            resp = ihttp.post(url, data={
                "act": "PagCountry"
            })
            if resp.status_code == 200:
                datas = resp.json()
                for data in datas:
                    areaCodeToCountry[str(data['Country_Area'])] = data['Country_ID']
        except:
            pass

    def send(self, action, params):
        params['act'] = action
        if action != "login":
            params["token"] = self.token
        res = self.loopSendGet(self.server_url, params)
        if res.ok:
            try:
                return res.text.split("|")
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
        params = {
            "ApiName": self.account,
            "PassWord": self.password,
        }
        data = self.send("login", params)
        if self.isOk(data):
            self.token = data[1]
            self.hasYuE = True
        return self.hasYuE

    '''
    http://www.firefox.fun/yhapi.ashx?act=getPhone&token=token&iid=1001&did=&country=&operator=&provi=&city=&seq=0&mobile=
    1|pkey|提取时间|国家代码|运营商|归属地|端口号|手机号
    '''

    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "country": self.country,
                "iid": self.service
            }
            for i in range(10):
                data = self.send("getPhone", params)
                if self.isOk(data):
                    self.tzid = data[1]
                    self.cellNum = data[-1]
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
    http://www.firefox.fun/yhapi.ashx?act=getPhoneCode&token=${token}&pkey=${pkey}
    1|验证码数字|完整短信内容
    '''

    def querySMS(self):
        # if self.msg is not None:
        self.msg = None
        params = {
            "pkey": self.tzid
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60 * 3
        for i in range(10):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send("getPhoneCode", params)
            if self.isOk(data):
                self.msg = self.parseDYSMSCode(data[1])
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
            "pkey": self.tzid,
        }
        result = self.send("setRel", params)

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
class FirefoxClient2(FirefoxClient):
    # 如果对接卡商开通了apiReturn反馈接口,需要通过反馈接口反馈是否注册成功,以保证收到短信后如果注册失败不扣费
    # (固定值 0：成功，-1：失败，-2：验证码超时，-3：号码已注册)，其他信息请直接输入
    def apiReturn(self, remark):
        params = {
            "pkey": self.tzid,
            "remark": remark,
        }
        result = self.send("apiReturn", params)
