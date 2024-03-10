import os
import pickle
import zlib
import base64
import random

from .device_info import DeviceInfo


class Session(object):
  def __init__(self):
    self.account: str = None
    self.user_id: int = 0
    self.proxy: str = None

    self.brand: str = None
    self.model: str = None
    self.sdk_release: str = None
    self.sdk: int = 0


  def __str__(self):
    return "Session:[id:%s, proxy:%s]" % (self.id, self.proxy)
  
  def __getstate__(self):
    state = self.__dict__.copy()
    return state

  def __setstate__(self, state):
    self.__dict__.update(state)
    self.seq = None

  def merge_login_result_info(self, data: dict):
    self.user_id = data["id"]
    self.account = str(self.user_id)

  def merge_device_info(self, d: DeviceInfo):
    self.brand = d.brand
    self.model = d.model
    self.sdk_release = d.sdk_release
    self.sdk = d.sdk

  @property
  def id(self):
    return self.account

  def dumps(self):
    return str(base64.b64encode(zlib.compress(pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL))), encoding="utf-8")

  @staticmethod
  def loads(data):
    return pickle.loads(zlib.decompress(base64.b64decode(data)))

  @staticmethod
  def get_expire_second(self):
    return 60 * 60 * 24 * 3
