import time

import names
import os
from loguru import logger

from app.libs import ihttp
from app.sms import ismsManager
from app.state.loop import bb, tt
import app.libs.pyautoguiUtils as pyautoguiUtils
from app.task import core
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from app.utils import ip_utils, browser_utils, proxy_utils, win_utils, selenium_utils


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

    # TODO:检查任务中参数
    return "jump_to_homepage"


def jump_to_homepage():
    res = core.openBrowser()
    # res = open_browser_local()
    if res == 'timeout':
        bb.result["msg"] = "打开浏览器超时"
        return "task_failed"
    if res == 'failed':
        bb.result["msg"] = "打开浏览器失败"
        return "task_failed"
    if res == 'success':
        print(bb.browser + '_' + bb.appType)
        if not bb[bb.browser + '_' + bb.appType]:
            bb.result["msg"] = "获取任务浏览器driver失败"
            return "task_failed"
        driver = bb[bb.browser + '_' + bb.appType]
        # driver.get(core._get_url(bb.appType))
        # 直接打开发布作品页面
        driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
        return "check_login"


def check_login():
    driver = bb[bb.browser + '_' + bb.appType]
    if "login" in driver.current_url:
        driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
        bb.result["msg"] = "获取任务浏览器driver失败"
        return "failed"
    return "upload_video"


def upload_video():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('video'):
        bb.result["msg"] = "获取视频失败"
        return "task_failed"

    filepath = bb.task['data']['video']
    whole_path = os.path.join(bb.config.resBak, filepath)
    logger.info("xhs_send_post:upload_video  whole_path - {}", whole_path)

    try:
        element = selenium_utils.find_element(driver=driver, param='//input[@type="file"]')
        # element = driver.find_element(By.XPATH, '//input[@type="file" and @class="upload-input"]')
        if element:
            # print(element)
            element.send_keys(whole_path)
            return "wait_upload_video"
    except Exception as e:
        logger.error("{} xhs_send_post:upload_video error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "上传视频失败,error "
        return "failed"

    bb.result["msg"] = "上传视频失败"
    return "failed"


def wait_upload_video():
    driver = bb[bb.browser + '_' + bb.appType]

    try:
        element = driver.find_element(By.XPATH, '//span[@class="btn-content" and text()="详情"]')
        if element:
            return "input_post_title"
    except Exception as e:
        logger.error("{} xhs_send_post:wait_upload_video error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "上传视频超时"
        return "failed"

    bb.result["msg"] = "上传视频超时"
    return "failed"


def input_post_title():
    if not bb.task['data'].get('title'):
        return "input_post_desc"

    title = bb.task['data']['title']

    driver = bb[bb.browser + '_' + bb.appType]
    # element = selenium_utils.find_element(driver=driver, param='//input[@placeholder="填写标题，可能会有更多赞哦～"]')
    element = selenium_utils.find_element(driver=driver, param='//input[@class="c-input_inner"]')
    if element:
        element.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.5)
        element.send_keys(title)
        return "input_post_desc"
    else:
        bb.result["msg"] = "输入标题失败"
        return "failed"


def input_post_desc():
    driver = bb[bb.browser + '_' + bb.appType]
    # desc为空 不填
    if not bb.task['data'].get('desc'):
        return "add_location"

    desc = bb.task['data']['desc']
    content_list = pyautoguiUtils.deal_content_to_list(desc)

    try:
        element = selenium_utils.find_element(driver=driver, param='//p[@id="post-textarea"]')
        if not element:
            bb.result["msg"] = "获取内容输入框失败"
            return "failed"

        for content in content_list:
            element.send_keys(content)
            if content.startswith(('@', '#')):
                time.sleep(3)
                element.send_keys(Keys.ENTER)
                time.sleep(1)

        return "add_location"

    except Exception as e:
        logger.error("{} xhs_send_post:input_post_desc error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "输入正文内容失败:\n" + str(e)
        return "task_failed"


def add_location():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('location'):
        return "set_who_can_see"
    location = bb.task['data']['location']

    try:
        element = selenium_utils.find_element(driver=driver, param='//input[@class="single-input"]')
        if element:
            element.send_keys(location)
            time.sleep(2)
            element = selenium_utils.find_element(driver=driver, param='//input[@class="single-input"]/following-sibling::div[1]/ul/li')
            if element:
                element.click()
                return "set_who_can_see"
            else:
                bb.result["msg"] = "选择地点失败：无匹配结果"
                return "failed"
        else:
            bb.result["msg"] = "选择位置失败:未获取到地点输入框"
            return "failed"
    except Exception as e:
        logger.error("{} xhs_send_post:add_location error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "选择位置失败:\n" + str(e)
        return "task_failed"


def set_who_can_see():
    driver = bb[bb.browser + '_' + bb.appType]
    # 不设置或者未0直接跳过 因为默认就是公开
    if not bb.task['data'].get('who_can_see'):
        return "pub_time"
    who_can_see = bb.task['data']['who_can_see']
    if who_can_see == '0':
        return "pub_time"
    else:
        try:
            element = selenium_utils.find_element(driver=driver, param='//input[@name="role" and @type="radio" and @value="1"]/..')
            if element:
                element.click()
                return "pub_time"
        except Exception as e:
            logger.error("{} xhs_send_post:set_who_can_see error - {}", bb.task['taskId'], e)
            bb.result["msg"] = "权限设置失败:\n" + str(e)
            return "failed"
    bb.result["msg"] = "权限设置失败"
    return "failed"


def pub_time():
    driver = bb[bb.browser + '_' + bb.appType]
    # 10位时间戳
    if not bb.task['data'].get('pub_time'):
        return "pub"
    pubTime = bb.task['data'].get('pub_time')
    if type(pubTime) == int:
        pubTime = str(pubTime)
    if len(pubTime) == 13:
        pubTime = pubTime[:10]
    if len(pubTime) != 10:
        bb.result["msg"] = "发布时间错误"
        return "task_failed"
    pubTime = int(pubTime)
    nowTime = time.time()
    nowTime = int(nowTime)
    if pubTime < nowTime + (1 * 60 * 60 + 5 * 60) or pubTime > nowTime + (14 * 24 * 60 * 60 - 5 * 60):
        bb.result["msg"] = "发布时间必须为至少一小时后，且小于十四天"
        return "task_failed"

    pubTime = float(pubTime)
    publishTime = time.strftime('%Y-%m-%d %H:%M', time.localtime(pubTime))

    try:
        element = selenium_utils.find_element(driver=driver, param='//input[@name="time" and @type="radio" and @value="1"]/..')
        if element:
            element.click()
            time.sleep(1)
            element = selenium_utils.find_element(driver=driver, param='//input[@placeholder="请选择日期"]')
            if element:
                element.send_keys(Keys.CONTROL, 'a')
                time.sleep(0.5)
                element.send_keys(publishTime)
                time.sleep(0.5)
                element.send_keys(Keys.ENTER)
                return "pub"
            else:
                bb.result["msg"] = "设置定时发布失败:输入时间失败"
                return "failed"
        else:
            bb.result["msg"] = "设置定时发布失败:获取定时发布单选框失败"
            return "failed"

    except Exception as e:
        logger.error("{} xhs_send_post:pub_time error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "设置定时发布失败:\n" + str(e)
        return "failed"


def pub():
    # return "check_pub"
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        element = driver.find_element(By.CLASS_NAME, 'publishBtn')
        if element:
            element.click()
            return "check_pub"
    except Exception as e:
        logger.error("{} xhs_send_post:pub error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "点击发布按钮失败:\n" + str(e)
        return "failed"
    bb.result["msg"] = "点击发布按钮失败"
    return "failed"


def check_pub():
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        element = selenium_utils.find_element(driver=driver, param='//div[@class="success-container"]')
        if element:
            logger.info("{} xhs_send_post:check_pub success - {}", bb.task['taskId'], element)
            return "task_success"
    except Exception as e:
        logger.error("{} xhs_send_post:pub error - {}", bb.task['taskId'], e)
        bb.result["msg"] = "点击发布按钮失败:\n" + str(e)
        return "failed"
    bb.result["msg"] = "发布失败"
    return "failed"


def task_failed():
    close_browser()
    bb.result["code"] = -1
    resp = ihttp.post(
        url=f"{bb.config.gatewayServerURL + bb.config.feedbackTask}", json={
            "machineId": tt.get_machine_id() + "," + bb.browser + "," + bb.appType + "," + ip_utils.get_mac() + "," + ip_utils.get_local_ip(),
            "taskId": bb.task['taskId'],
            "result": {
                "code": -1,
                "msg": bb.result["msg"]
            }
        }
    )
    return "success"


def task_success():
    close_browser()
    resp = ihttp.post(
        url=f"{bb.config.gatewayServerURL + bb.config.feedbackTask}", json={
            "machineId": tt.get_machine_id() + "," + bb.browser + "," + bb.appType + "," + ip_utils.get_mac() + "," + ip_utils.get_local_ip(),
            "taskId": bb.task['taskId'],
            "result": {
                "code": 0,
                "msg": 'success'
            }
        }
    )
    return "success"

def close_browser():
    name = bb.browser + '_' + bb.appType + '.exe'
    browser_utils.close_browser(name)


def open_browser_local():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:16801")
    driver = webdriver.Chrome(options=chrome_options)
    bb["chrome_1_dy"] = driver
    return "success"
