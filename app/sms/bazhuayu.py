import requests
from .isms import ISMS
from app.libs import ihttp
import time
import re
from urllib.parse import quote
from loguru import logger

'''
200 成功
204 当前业务繁忙，没有手机号可供使用，请稍后重试
205 业务查询为空
206 账号余额不足
207 验证码超时
208 账号禁用
209 秘钥错误
210 Token 错误
213 当前手机号正在执行其他业务，请稍后重试
214 拉取手机号次数不足，请联系平台管理人员
216 手机号已经下线
219 无权限使用该国家手机号
220 垄断时间这个参数错误
'''
class BazhuayuClient(ISMS):
    def __init__(self, params, vpsID, serverPath):
        if params is None:
            params = {
                "area": {
                    "code": "63",
                    "name": "Philippines",
                    "abbr": "PH"
                }
            }
        super(BazhuayuClient, self).__init__(params, vpsID, serverPath)
        if not self.server_url: self.server_url = "http://api.ykwws.xyz:2086/registerApi/"
        self.country = self.data["area"]["abbr"]

    def login(self):
        # res = self.send({
        #     "act": "login",
        #     "ApiName": self.account,
        #     "PassWord": self.password
        # })
        # data = res.text.split("|")
        # if data[0] == "1":
        #     self.token = data[1]
        #     return True
        # return False
        return True

    '''
    http://api.ykwws.xyz:2086/registerApi/getMobile?uid=${account}&size=10&pid=${service}&sign=${password}&cuy=${country}&include=1&ctype=1
    {
        “code”:”0”, //错误码
        “msg”:”success”, //错误信息
        “orderId”:”订单编号”,  //获取验证码时会用到
        “data”:[
            86150125893，
            86150125894，
        ]
    }
    '''
    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "uid": self.account,
                "size": 1,
                "pid": self.service,
                "sign": self.password,
                "cuy": self.country,
                "include": 1,
                "ctype": 1
            }
            for i in range(10):
                res = self.send("getMobile", params)
                if res["code"] == 0:
                    self.orderId = res["orderId"]
                    self.cellNum = str(res["data"][0])
                    errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                    if errormessage is None:
                        break
                    else:
                        self.phoneRelease("该手机号已经使用过")
                time.sleep(3)
            if self.cellNum is None:
                return None
            self.logPhone(self.cellNum)
        return "+" + self.cellNum

    '''
    http://api.ykwws.xyz:2086/registerApi/getMsg?uid=${account}&orderId=${orderId}&sign=${password}
    {
        “error”:”0”,
        “msg”:”success”,///error=0时不会返回此字段
        “data”:[
        {
            “hm”:”xxxxxx”, --号码 带区号
            “code”:1111, ---验证码
            “txt”：“xxx”,---短信内容
            “country”:”IN”,---号码所属的国家简称
            “time”:”1234567894561”,---13位，表示平台收到验证码的时间戳
        }
        ] 
    }
    '''
    def querySMS(self):
        self.msg = None
        params = {
            "orderId": self.orderId,
        }

        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = self.send("getMsg", params)
            if res.get("data") != None:
                self.msg = res['data'][0]['code']
                return self.msg
            time.sleep(5)
        return self.msg

    '''
    http://api.ykwws.xyz:2086/registerApi/getUserInfo&uid=${account}&sign=${password}
    {
        “code”:”0”,
        “msg”:”success”
        “data”:{
            “userName”:”xxxxxx”, 
            “score”:{
                [
                    {gold:积分1, pid:项目1},
                    {gold:积分2,pid:积分2},
                    ...
                ]
            }
            “createTime”:”2020-09-08”
        }
    }
    '''
    def getUserInfo(self):
        params = {

        }
        res = self.send("getUserInfo", params)
        if res["code"] == 0:
            return res["data"]
        return None

    def send(self, action, params):
        params["uid"] = self.account
        params['sign'] = self.password
        res = self.loopSendGet(f'{self.server_url}{action}', params)
        if res.ok:
            try:
                return res.json()
            except Exception:
                pass
        return None

    def phoneRelease(self, status):
        # for i in range(3):
        #     result = self.send({
        #         "act": "addBlack",
        #         "token": self.token,
        #         "pid": self.orderId,
        #         "reason": quote(status),
        #     })
        #     data = result.text.split("|")
        #     if data[0] == "1":
        #         self.cellNum = None
        #         return
        #     time.sleep(3)
        pass

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease("业务注册完成")
        elif status == "failed":
            self.phoneRelease("业务注册失败")
        else:
            self.phoneRelease("业务注册失败")
        self.cellNum = None
