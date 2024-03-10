import json
import time

from .isms import ISMS
from app.state.loop import bb
from loguru import logger

class SmsPlatform(ISMS):
  def __init__(self, params, vpsID, serverPath, smsUrl):
    if params is None:
      params = {
        "area": {
          "code": "63",
          "name": "Philippines",
          "abbr": "PH"
        }
      }
    super(SmsPlatform, self).__init__(params, vpsID, serverPath)
    self.country = self.data["area"]["abbr"]
    self.smsUrl = smsUrl
    self.areas = {}
    with open('area.json', 'r', encoding='utf8') as fp:
      data = json.load(fp)
      for item in data:
        self.areas[item["code"]] = item

  def send(self, action, params):
    params["phonePlatform"] = self.data
    res = self.loopSendPost(f'{self.smsUrl}{action}', params)
    if res.ok:
      try:
        return res.json()
      except Exception:
        pass
    return None

  def login(self):
    params = {

    }
    res = self.send(bb.config.smsPlatformLoginUrl, params)
    if res and res['code'] == 0:
      if res.get('data').get("token") is not None:
        self.token = res['data']['token']
      return True
    logger.info(res)
    raise Exception(res.get('msg'))

  def getCellNum(self):
    if self.cellNum is None:
      res = {}
      params = {
        'token': self.token
      }
      for i in range(10):
        res = self.send(bb.config.smsPlatformGetPhoneUrl, params)
        if res and res['code'] == 0:
          self.cellNum = res['data']['code'] + res['data']['phone']
          self.pkey = res['data']
          self.data["area"] = self.areas[res["data"]["code"]]
          self.area = self.areas[res["data"]["code"]]
          errormessage = self.checkPhone(res['data']['phone'], res['data']['code'])
          if errormessage is None:
            break
          else:
            self.phoneRelease("该手机号已经使用过")
        time.sleep(3)
      if self.cellNum is None:
        logger.info(res.get('data'))
        return None
      self.logPhone(self.cellNum)
    return "+" + self.cellNum

  def querySMS(self):
    self.msg = None
    params = {
      'token': self.token,
      "pkey": self.pkey,
    }
    timeout = int(round(time.time() * 1000)) + 1000 * 50
    for i in range(45):
      if int(round(time.time() * 1000)) > timeout:
        break
      res = self.send(bb.config.smsPlatformGetPhoneCodeUrl, params)
      if res and res.get('code') == 0 and res.get('data') is not None:
        self.msg = self.parseDYSMSCode(res['data'])
        return self.msg
      time.sleep(5)
    return self.msg

  def phoneRelease(self, status):
    params = {
        "token": self.token,
        "pkey": self.pkey,
        "status": status
    }
    if self.cellNum is not None and status == "success":
        self.send(bb.config.smsPlatformAddBlackUrl, params)
    else:
        self.send(bb.config.smsPlatformSetRelUrl, params)
    self.cellNum = None

  def add2BlackList(self, status, msg):
    if self.cellNum is not None:
        self.logPhone(self.cellNum)
        self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
    self.phoneRelease(status)
