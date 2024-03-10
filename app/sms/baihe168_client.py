from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger


class Baihe168Client(ISMS):
    def __init__(self, params, vpsID, serverPath):
        super(Baihe168Client, self).__init__(params, vpsID, serverPath)
        if self.server_url is None: self.server_url = "http://api.baihe168.vip"

    def send(self, action, params):
        if action != "get_amount":
            params["p_id"] = self.service
        params["token"] = self.token
        res = self.loopSendGet(f'{self.server_url}/{action}', params)
        if res.ok:
            try:
                return res.json()
            except Exception:
                pass
        return None

    '''
     * url : get_amount?token=登陆返回的令牌
     * response: { "code": 1, "msg": "获取成功", "time": "1603157867", "data": { "amount": 8.235 } }
    '''

    def getBalance(self):
        action = 'get_amount'
        params = {}
        data = self.send(action, params)
        if data is not None:
            if data['code'] == 1:
                return data['data']['amount']

        return 0

    def login(self):
        if self.token:
            balance = self.getBalance()
            return balance > 0
        return False

    '''
     * url: get_hone?token=登录时返回的令牌&p_id=项目ID
     * response:
     * {
     *   "code": 1,
     *   "msg": "获取成功1个",
     *   "time": "1603158524",
     *   "data": [ {
     *     "phone": "17069456682",
     *     "area": "江西,南昌,虚拟",
     *     "add_time": 1603158524,
     *     "expira_time": 1603159484,
     *     "order_number": "1603158524_3060"
     *   } ]
     * }
    '''

    def getCellNumSend(self):
        action = "get_phone"
        params = {}
        data = self.send(action, params)
        if data is not None:
            if data['code'] == 1:
                phone = data['data'][0]
                self.orderId = phone['order_number']
                self.cellNum = phone['phone']

    def getCellNum(self):
        if self.cellNum is None:
            self.loopGetCellNum()

        return "+" + self.area['code'] + self.subAreaCode(self.cellNum)

    '''
     * url: get_message?token=登陆返回的令牌&g_id=项目ID&phone=取到的手机号码&order_number=订单号
     * response:
     * {
     *   "code": 1,
     *   "msg": "获取成功",
     *   "time": "1603163263",
     *   "data": {
     *     "order_number": "1603163231_3060",
     *     "phone": "17069456314",
     *     "sms": "【Instagram】请使用 356 247 验证你的 Instagram 帐户。",
     *     "yzm": " 247 验证"
     *   }
     * }
     * {
     *   "code": 0,
     *   "msg": "正在等待获取",
     *   "time": "1603160578",
     *   "data": null
     * }
    '''

    def querySMS(self):
        action = 'get_message'
        params = {
            "phone": self.cellNum,
            "order_number": self.orderId,
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send(action, params)
            if data is not None and data['code'] == 1:
                self.msg = self.parseDYSMSCode(data['data']['sms'].replace(" ", ""))
                break
            time.sleep(3)

        return self.msg

    '''
     * url: release?token=登录时返回的令牌&p_id=项目ID&phone=获取的手机号&order_number=订单号
     * response
     * {
     *   "code": 1,
     *   "msg": "释放成功",
     *   "time": "1603161052",
     *   "data": null
     * }
    '''

    def phoneRelease(self, status):
        action = "release"
        params = {
            "phone": self.cellNum,
            "order_number": self.orderId,
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
            action = 'shielding'
            params = {
                "phone": self.cellNum,
                "order_number": self.orderId,
            }
            for i in range(3):
                if self.send(action, params) is not None: break
        else:
            self.phoneRelease()
        self.cellNum = None
        self.orderId = None
