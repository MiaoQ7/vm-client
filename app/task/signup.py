import names
from loguru import logger

from app.libs import ihttp
from app.sms import ismsManager
from app.state.loop import bb, tt
from app.utils import ip_utils


def start():
    ihttp.reset_session()
    bb.retryCount = 0
    bb.result = {"msg": None}
    bb.socks5 = None
    bb.javaSessions = None
    bb.webSessions = None
    bb.ip = None
    bb.username = None
    bb.cellCode = None
    bb.cellNum = None
    bb.payload = {
    }
    nextStep = {
        "bazhuayu-random-area": "fetch_phone",
        "snails_random": "fetch_phone",
    }
    try:
        nickname = bb.account['nickname']
        names = nickname.split(" ")
        if names[0] and names[1]:
            bb.account["payload"]['firstName'] = names[0]
            bb.account["payload"]['lastName'] = names[1]
    except:
        pass
    if not bb.account["payload"].get("firstName") or not bb.account["payload"].get("lastName"):
        bb.result["msg"] = "昵称获取失败需要格式：【firstName lastName】"
        return "task_failed"
    return nextStep.get(bb.phonePlatform["platformCode"], "success")


def fetch_phone():
    del bb.result["msg"]  # 删除上一轮的默认错误信息
    if bb.cellNum:
        return "success"
    try:
        bb.activate_client = ismsManager.getClient(bb.phonePlatform, tt.get_machine_id(), bb.config.taskServerURL,
                                                   bb.config.smsPlatformURL)
    except Exception as err:
        ip_utils.release22()
        logger.exception(err)
        bb.result["msg"] = str(err)
        return "task_failed"
    cellNum = bb.activate_client.getCellNum()
    if cellNum is None:
        # 没取到手机号禁用卡商
        ihttp.get("%s%s/%s" % (bb.config.taskServerURL, bb.config.disablePhoneCodeURL, bb.phonePlatform["_id"]))
        ip_utils.release22()
        logger.info('获取手机号码失败')
        bb.result["msg"] = "获取手机号码失败"
        return "task_failed"
    logger.info(f"cellNum---------{cellNum}")

    if getattr(bb.activate_client, "area", None):
        # 最好是从卡商里获取areaCode,但是现在有部分卡商实现代码未调用super().__init__()接口,所以需要检测一下是否有area字段
        bb.cellCode = bb.activate_client.area["code"]
        bb.phonePlatform["socks5AreaCode"] = bb.activate_client.area["abbr"]
    else:
        bb.cellCode = bb.phonePlatform["area"]["code"]
    bb.cellNum = cellNum[len(bb.cellCode) + 1:]
    if not bb.socks5:
        return "get_proxy"
    return "success"


def gen_device_info():
    # bb.device = DeviceInfo()
    # bb.device.rand_some_info()
    # bb.device.setup_sim_info(f"+{bb.cellCode}{bb.cellNum}")
    return "success"


def request_code():
    proxy = bb.socks5
    proxy = proxy[proxy.index("//") + 2:]
    name_end = proxy.find(":")
    pwd_end = proxy.index("@")
    host_end = proxy.rfind(":")
    if proxy.startswith("@"):
        bb.proxy = {
            "ip": proxy[pwd_end + 1:host_end],
            "port": proxy[host_end + 1:],
        }
    else:
        bb.proxy = {
            "ip": proxy[pwd_end + 1:host_end],
            "port": proxy[host_end + 1:],
            "username": proxy[:name_end],
            "password": proxy[name_end + 1:pwd_end]
        }

    if len(bb.phonePlatform["area"]["abbr"]) > 2:
        bb.phonePlatform["area"]["abbr"] = bb.phonePlatform["area"]["abbr"][:2]

    if bb.account.get("googleToken") is not None and bb.account.get("googleToken") != "":
        bb.payload['googleToken'] = bb.account.get("googleToken")

    resp = ihttp.post(
        url=f"{bb.config.gatewayServerURL}{bb.config.regRequestCodeURL}",
        json={
            "proxy": bb.proxy,
            "countryCode": bb.phonePlatform["area"]["abbr"].lower(),
            "phone": f'{bb.cellNum}',
            "password": bb.account["payload"]["password"],
            "firstName": bb.account["payload"]['firstName'],
            "lastName": bb.account["payload"]['lastName'],
            "googleToken": bb.account.get("googleToken"),
        },
        timeout=600
    )
    if resp.ok:
        data = resp.json()
        if data["code"] == 0:
            bb.session = data["data"]
            if data.get("hasCaptcha") is not None:
                bb.payload['hasCaptcha'] = data.get("hasCaptcha")
            return "success"
        elif data["code"] == -1:
            bb.result["msg"] = data["msg"]
            return "task_failed"
        else:
            if ('errors' in data['msg'] or bb.retryCount > 5):
                try:
                    bb.result["msg"] = "code:" + str(data["code"]) + " msg:" + data["msg"]
                except:
                    bb.result["msg"] = data["msg"]
                return "task_failed"
            bb.socks5 = None
            bb.retryCount += 1
            return "get_proxy"
    else:
        bb.result["msg"] = '发送验证码请求失败'
    return "failed"


def request_resend():
    response = ihttp.post(
        url=f"{bb.config.gatewayServerURL}{bb.config.regRequestResendCodeURL}",
        json={
            "proxy": bb.proxy,
            "session": bb.session,
            "code": "",
        }
    )

    if response.ok:
        data = response.json()
        if data["code"] == 0:
            bb.session = data["data"]
    return "success"


def request_register():
    code = bb.activate_client.querySMS()  # 这里有等待的逻辑
    if code is None:
        sms_resend_count = bb.result.get("sms_resend_count", 1)
        if sms_resend_count < 3:
            logger.info("接码失败{}次", sms_resend_count)
            bb.result["sms_resend_count"] = sms_resend_count + 1
            return "resend"

        logger.info('获取验证码失败')
        bb.result["msg"] = "获取验证码失败"
        return "task_failed"

    resp = ihttp.post(
        url=f"{bb.config.gatewayServerURL}{bb.config.regRequestRegisterURL}",
        json={
            "proxy": bb.proxy,
            "code": code.replace("-", ""),
            "session": bb.session,
        },
        timeout=600
    )
    if resp.ok:
        data = resp.json()
        if data["code"] == 0:
            bb.payload = {
                **bb.payload,
                "session": data["data"],
            }
            return "success"
        else:
            try:
                bb.result["msg"] = "code:" + str(data["code"]) + " msg:" + data["msg"]
            except:
                bb.result["msg"] = data["msg"]
            return "task_failed"
    return "failed"


def task_failed():
    try:
        bb.activate_client.add2BlackList("failed", None)
        ip_utils.release22()
        resp = ihttp.get(url=f"{bb.config.taskServerURL + bb.config.releaseSignupFriendURL}/{tt.get_machine_id()}")
    except Exception as e:
        pass

    area = None
    if bb.cellNum is not None:
        if hasattr(bb.activate_client, "area"):
            area = bb.activate_client.area
        else:
            area = bb.phonePlatform["area"]

    logger.info("task_failed bb.result: {}", bb.result)
    params = {
        "vpsID": tt.get_machine_id(),
        "result": "failed",
        "msg": bb.result.get("msg", "unknown"),
        "emulatorID": bb.cellNum,      # 用不带区号的手机号当emulatorID
        "payload": {
            # 如果注册失败,记录一下卡商
            "phonePlatform": bb.phonePlatform,
            "area": area,
        }
    }
    try:
        response = ihttp.post(f"{bb.config.taskServerURL + bb.config.feedbackURL}", json=params)
        if response.ok:
            data = response.json()
            if data["code"] == 1:
                return "success"
    except Exception as e:
        logger.error("task_success error: {}", e)
    return "failed"


def task_success():
    try:
        bb.activate_client.add2BlackList("success", None)
        ip_utils.release22()
        resp = ihttp.get(url=f"{bb.config.taskServerURL + bb.config.releaseSignupFriendURL}/{tt.get_machine_id()}")
    except Exception as e:
        pass

    logger.info("task_success bb.result: {}", bb.result)

    if hasattr(bb.activate_client, "area"):
        area = bb.activate_client.area
    else:
        area = bb.phonePlatform["area"]

    payload = {
        **bb.payload,
        # "nickname": bb.account["nickname"],
    }

    params = {
        "vpsID": tt.get_machine_id(),
        "result": "success",
        "msg": "成功",
        "emulatorID": f'{bb.cellNum}',      # 用不带区号的手机号当emulatorID
        "payload": {  # 用json传参 payload 不用序列化成字符串
            "wechat_id": bb.signupFriend["_id"],
            "increaseSignupFriend": False,
            "phonePlatform": bb.phonePlatform,
            "countryCode": bb.phonePlatform["area"]["code"],
            "phone": f'{bb.cellNum}',
            "ip": bb.ip,
            "hardware": bb.hardware,
            "area": area,
            **payload,
        }
    }
    try:
        response = ihttp.post(f"{bb.config.taskServerURL + bb.config.feedbackURL}", json=params)
        if response.ok:
            data = response.json()
            if data["code"] == 1:
                return "success"
    except Exception as e:
        logger.error("task_success error: {}", e)
    return "failed"
