import uuid
import time
from app.state.loop import bb, tt, fs
from app.libs import ihttp
from loguru import logger
from app.utils import ip_utils, browser_utils
import app.libs.pyautoguiUtils as pyautoguiUtils
import os
from app.utils import ip_utils, browser_utils, proxy_utils, win_utils
from app.task import core
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver import ActionChains


def start():
    ihttp.reset_session()
    bb.retryCount = 0
    bb.result = {"msg": None}
    if not bb.task.get("data"):
        bb.result["msg"] = "获取任务参数失败"
        return "failed"
    return "jump_to_homepage"

def jump_to_homepage():
    res = core.openBrowser()
    # res = open_browser_local()
    # print(bb)
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
        driver.get("https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web")
        return "upload_video"



def upload_video():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('video'):
        bb.result["msg"] = "获取视频失败"
        return "task_failed"
    filepath = bb.task['data']['video']
    whole_path = os.path.join(bb.config.resBak, filepath)
    try:
        element = driver.find_element(By.XPATH, '//input[@name="upload-btn" and @type="file"]')
        # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[3]/div/div/div/div[2]/div/div/div/div[3]/div/div/div/div/div/label/input[@type="file"]')
        if element:
            print(element)
            element.send_keys(whole_path)
            return "check_have_rec_tag"
    except Exception as e:
        print(e)
        bb.result["msg"] = "上传视频失败,error "
        return "task_failed"
    bb.result["msg"] = "上传视频失败"
    return "failed"


def check_have_rec_tag():
    driver = bb[bb.browser + '_' + bb.appType]
    list = []
    try:
        element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[4]/div[2]/div[1]')
        if element:
            element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[4]/div[2]/div[3]')
            if element:
                ActionChains(driver).move_to_element(element).perform()
                time.sleep(1)
            element = driver.find_elements(By.XPATH, '//div[@class="semi-tag-content"]')
            if element and len(element) > 0:
                for eee in element:
                    tmp = str(eee.text).strip()
                    if tmp.startswith("#"):
                        list.append(tmp)
                if len(list) > 0:
                    bb.result['data'] = list
                    return "task_success"
                else:
                    bb.result["msg"] = "获取到的tag数量为0"
                    return "task_failed"
    except Exception as e:
        print(e)
        bb.result["msg"] = "未检测到出现推荐话题"
        driver.refresh()
        time.sleep(1)
        # driver.switch_to.alert.accept()
        return "failed"

    bb.result["msg"] = "未检测到出现推荐话题"
    driver.refresh()
    time.sleep(1)
    # driver.switch_to.alert.accept()
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
                "msg": 'success',
                "data": bb.result['data']
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