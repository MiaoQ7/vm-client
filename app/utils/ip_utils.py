from app.state.loop import bb,tt,fs
from app.libs import ihttp
from loguru import logger
import getmac

def check(ip):
    if ip is None:
        return False

    rsp = ihttp.post(bb.config.ipServerURL + bb.config.checkIpURL, json={
        "proxyIp": ip,
        "serverId": bb.config.ipServerId,
    })
    if rsp.ok:
        data = rsp.json()
        if "code" in data and data["code"] != 1:
            return True
    return False

def release(ip):
    if ip is None:
        return False

    rsp = ihttp.post(bb.config.ipServerURL + bb.config.releaseIpURL, json={
        "proxyIp": ip,
        "serverId": bb.config.ipServerId,
    })
    if rsp.ok:
        data = rsp.json()
        if "code" in data and data["code"] == 0:
            return True
    return False

def release22():
    # 如果没有username代表已经释放
    if bb.username is None:
        return True

    params = {
        "proxyAccount": {
            "account": bb.phonePlatform['ipPlatform'],
            "username": bb.username or '',
        }
    }
    logger.info("release_aggregationProxy params: {}", params)
    rsp = ihttp.post(f'{bb.config.ipPlatformURL}/api/socks5/releaseSocks', json=params)
    logger.info("release_aggregationProxy resp: {}", rsp)

    if rsp.ok:
        data = rsp.json()
        if "code" in data and data["code"] == 0:
            bb.username = None
            return True
    return False

def get_local_ip():
    import socket

    # 获取主机名
    hostname = socket.gethostname()

    # 根据主机名获取IP地址列表
    ip_list = socket.getaddrinfo(hostname, None)

    # 提取第一个非空的IPv4地址
    for ip in ip_list:
        if ':' not in ip[4][0]:
            if ip[4][0] != '192.168.123.1':
                local_ip = ip[4][0]
                break
    else:
        # 如果没有找到合适的IPv4地址，则返回None
        local_ip = None

    return local_ip

def get_mac():
    if bb.mac:
        pass
    else:
        bb.mac = getmac.get_mac_address().upper()
    return bb.mac