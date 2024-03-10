import requests
from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

areaCodeToCountry = {
    "Russia": "russia",
    "Ukraine": "ukraine",
    "Kazakhstan": "kazakhstan",
    "China": "china",
    "Kyrgyzstan": "kyrgyzstan",
    "United States": "usa",
    "Poland": "poland",
    "Nigeria": "nigeria",
    "Macau (China)": "macau",
    "South Africa": "southafrica",
    "Romania": "romania",
    "Estonia": "estonia",
    "Azerbaijan": "azerbaijan",
    "United Kingdom": "england",
    "Canada": "canada",
    "Malaysia": "malaysia",
    "Germany": "germany",
    "Spain": "spain",
    "Indonesia": "indonesia",
    "Vietnam": "vietnam",
    "Thailand": "thailand",
    "India": "india",
    "Brazil": "brazil",
    "Turkey": "turkey",
}
class FiveSimClient(ISMS):

    def __init__(self, params, vpsID, serverPath):
        global areaCodeToCountry
        if params is None:
          params = {
            "area": {
              "code": "7",
              "name": "Russia"
            }
          }
        self.data = params
        self.server_url = params.get("serverUrl", "https://5sim.net")
        areaName = self.data.get("area").get("name")
        self.country = areaCodeToCountry.get(areaName)
        if self.country is None:
          raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.token = params.get("password", "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY0NTQ5MDksImlhdCI6MTYwNDkxODkwOSwicmF5IjoiMmFkNWIwMjk3YzQ0Yjc0NWQ3MTU5NzI5ODdlYjljNzIiLCJzdWIiOjEzOTIxMX0.LHws0oDTTvyhO_hQaqaeKotCx5p-xdANwPn-zOSieT8rCVOyRx63Hqvksz5taI5ADZ2qGmwFN7NAGVik75zd7iGwDjM1htwajxn7SKFdqFMAk254_UwnifjtrdpRr0O8P_A0VOUCJMQAt892b6mKx74YxCA0P5lLm_e5dalbJ-tZqToahaBtA6pHuhowngOZO-Gdq7xFDMvp0W3rs9n6BWswnfTZLUT76vOzAkUWlcE07R9haCt_XDRgzUKkQfMQaFW4moP6cOrYhIC5-ADQk2WbUGL7b-dj5CsTP0RI0Tq5etdXc6401SEHT1JGw2cojWiZN2cPMhywxcEVnCY2IA")
        # self.token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY0NTQ5MDksImlhdCI6MTYwNDkxODkwOSwicmF5IjoiMmFkNWIwMjk3YzQ0Yjc0NWQ3MTU5NzI5ODdlYjljNzIiLCJzdWIiOjEzOTIxMX0.LHws0oDTTvyhO_hQaqaeKotCx5p-xdANwPn-zOSieT8rCVOyRx63Hqvksz5taI5ADZ2qGmwFN7NAGVik75zd7iGwDjM1htwajxn7SKFdqFMAk254_UwnifjtrdpRr0O8P_A0VOUCJMQAt892b6mKx74YxCA0P5lLm_e5dalbJ-tZqToahaBtA6pHuhowngOZO-Gdq7xFDMvp0W3rs9n6BWswnfTZLUT76vOzAkUWlcE07R9haCt_XDRgzUKkQfMQaFW4moP6cOrYhIC5-ADQk2WbUGL7b-dj5CsTP0RI0Tq5etdXc6401SEHT1JGw2cojWiZN2cPMhywxcEVnCY2IA"
        self.product = params.get("projectId", "whatsapp")
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "five_sim")
        self.vpsID = vpsID
        self.serverPath = serverPath
        self.orderId = None

    def login(self):
        res = self.send("/v1/user/profile")
        if res.status_code == 200:
          self.hasYuE = res.json()["balance"] > 0
        return self.hasYuE

    def getCellNum(self):
        if self.cellNum is None:
            for i in range(10):
                res = self.send(f"/v1/user/buy/activation/{self.country}/any/{self.product}")
                if res.status_code == 200:
                    data = res.json()
                    self.orderId = data["id"]
                    self.cellNum = data["phone"]
                    errormessage = self.checkPhone(self.cellNum[len(self.data["area"]["code"]) + 1:], self.data["area"]["code"])
                    if errormessage is None:
                        break
                    else:
                        self.phoneRelease(8)
                time.sleep(3)
            self.logPhone(self.cellNum)
        return self.cellNum
       

    def querySMS(self):
        self.msg = None
       
        timeout = int(round(time.time() * 1000)) + 1000 * 50
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            res = self.send(f"/v1/user/check/{self.orderId}")
            if res.status_code == 200 and res.text is not None:
                data = res.json()
                try:
                    if data["status"] == "RECEIVED":
                        if len(data["sms"]) > 0:
                          sms = data["sms"][0]
                          self.msg = sms["code"]
                          return self.msg
                except Exception as e:
                    print(e)
            time.sleep(2)
        return self.msg

    def send(self, path, params={}):
        headers = {
          "Authorization": f"Bearer {self.token}",
          "Accept": "application/json",
        }
        for i in range(3):
            result = ihttp.get(self.server_url + path, params=params, headers=headers)
            result.encoding = "utf-8"
            # logger.info(f"status: {result.status_code}, content: {result.text}")
            if result.status_code == 200:
                return result
            time.sleep(3)

    def phoneRelease(self, status):
        for i in range(3):
            result = self.send(f"/v1/user/ban/{self.orderId}")
            if result.status_code == 200:
                self.cellNum = None
                return
            time.sleep(3)

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease(6)
        elif status == "failed":
            self.phoneRelease(8)
        else:
            self.phoneRelease(8)
        self.cellNum = None
