from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

areaCodeToCountry = {
    "44": 'gb',         # 英国
    "225": 'ci',        # 科特迪瓦
}

projectId2secretKey = {
}

class Client(ISMS):
    def __init__(self, params, vpsID, serverPath):
        super(Client, self).__init__(params, vpsID, serverPath)
        if self.server_url is None: self.server_url = "http://opapi.smspva.net/out/ext_api"
        self.country = areaCodeToCountry.get(self.area['code'], self.area['abbr'].lower())
        self.secretKey = projectId2secretKey.get(self.service, '')

    def send(self, action, params):
        if action != "getUserInfo":
            params["pid"] = self.service
        params["name"] = self.account
        params["pwd"] = self.password
        res = self.loopSendGet(f'{self.server_url}/{action}', params)
        if res.ok:
            try:
                return res.json()
            except Exception:
                pass
        return None

    '''
     * url : getUserInfo
     * response: { "code": 200, "msg": "Success", "data": { "username": "admin", "score": 100, "create_date": "2018-05-09 11:18:35" } }
    '''

    def getBalance(self):
        action = 'getUserInfo'
        params = {}
        data = self.send(action, params)
        if data is not None:
            if data['code'] == 200:
                return data['data']['score']

        return 0

    def login(self):
        if self.token:
            balance = self.getBalance()
            return balance > 0
        return False

    '''
     * url: getMobile?name=admin&pwd=123&cuy=cn&pid=123&num=5&noblack=0&serial=2&secret_key=123456&vip=null
     * response:
     * {
     *   "code": 200,
     *   "msg": "Success",
     *   "data": "+8613925467893"
     * }
     //返回值参考
     200：成功
     800：账号被封禁
     801：用户不存在
     802：用户名或密码错误
     803：用户名和密码不能为空
     902：传递的参数不正确
     903：无效的国家代码
     904：无效的项目ID
     906：手机号列表为空
     403：积分不足
     400：失败，系统异常
     907：vip_key错误
    '''

    def getCellNumSend(self):
        action = "getMobile"
        params = {
            'cuy': self.country,
            'num': 1,
            'noblack': 1,
            'serial': 2,
            'secret_key': self.secretKey,
            'vip': None,
        }
        data = self.send(action, params)
        if data is not None:
            if data['code'] == 200:
                self.cellNum = data['data']

    def getCellNum(self):
        if self.cellNum is None:
            self.loopGetCellNum()

        # return "+" + self.area['code'] + self.subAreaCode()
        return self.cellNum

    '''
     * url: getMsg?name=admin&pwd=123&pn=+8613500000000&pid=123&serial=2
     * response: 
     * {
     *   "code": 200,
     *   "msg": "Success",
     *   "data": "467893"
     * }
     //返回值参考
     200：成功
     800：账号被封禁
     801：用户不存在
     802：用户名或密码错误
     803：用户名和密码不能为空
     904：无效的项目ID
     905：无效的手机号码
     908：暂未查询到验证码，请稍后再试
     405：验证码获取失败，请查询数据列表，或联系管理员
    '''

    def querySMS(self):
        action = 'getMsg'
        params = {
            "pn": self.cellNum,
            "order_number": self.orderId,
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send(action, params)
            if data is not None and data['code'] == 200:
                self.msg = data['data']
                break
            time.sleep(3)

        return self.msg

    '''
     * url: passMobile?name=admin&pwd=123&pn=+8613500000000&pid=123&serial=2
     * response
     * {
     *   "code": 200,
     *   "msg": "Success",
     *   "data": ""
     * }
     //返回值参考
     200：成功
     800：账号被封禁
     801：用户不存在
     802：用户名或密码错误
     803：用户名和密码不能为空
     401：失败，无效操作
     904：无效的项目ID
     905：无效的手机号码
    '''

    def phoneRelease(self, status):
        action = "passMobile"
        params = {
            "pn": self.cellNum,
            'serial': 2,
        }
        for i in range(3):
            data = self.send(action, params)
            if data is not None: break
        self.cellNum = None
        self.orderId = None

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease()
        elif status == "failed":
            action = 'addBlack'
            params = {
                "pn": self.cellNum,
            }
            for i in range(3):
                if self.send(action, params) is not None: break
        else:
            self.phoneRelease()
        self.cellNum = None
        self.orderId = None
