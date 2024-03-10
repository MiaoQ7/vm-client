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
    print(bb)
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
        return "enter_creator"


def enter_creator():
    return "upload_video"
    # driver = bb[bb.browser + '_' + bb.appType]
    # try:
    #     element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/header/div/div/div[2]/div/pace-island/div/div[4]/div/div')
    #     if element:
    #         element.click()
    #         return "upload_video"
    # except Exception as e:
    #     print(e)
    #     try:
    #         xpath = '//*[@class="AdVRSdga"][6]'
    #         element = driver.find_element(By.XPATH, xpath)
    #         if element:
    #             element.click()
    #             return "upload_video"
    #     except Exception as e:
    #         print(e)
    #         bb.result["msg"] = "点击投稿进入创作者中心失败"
    #         return "task_failed"
    # bb.result["msg"] = "点击投稿进入创作者中心失败"
    # return "failed"


def upload_video():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('video'):
        bb.result["msg"] = "获取视频失败"
        return "task_failed"
    filepath = bb.task['data']['video']
    whole_path = os.path.join(bb.config.resBak, filepath)
    logger.info("dysend_post:upload_video  whole_path - {}", whole_path)
    # print("----" + whole_path)
    try:
        element = driver.find_element(By.XPATH, '//input[@name="upload-btn" and @type="file"]')
        # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[3]/div/div/div/div[2]/div/div/div/div[3]/div/div/div/div/div/label/input[@type="file"]')
        if element:
            print(element)
            element.send_keys(whole_path)
            return "wait_upload_video"
    except Exception as e:
        logger.exception("上传视频失败 {}", e)
        bb.result["msg"] = "上传视频失败,error "
        return "task_failed"
    bb.result["msg"] = "上传视频失败"
    return "failed"

def wait_upload_video():
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        element = driver.find_element(By.XPATH, '//section[text()="检测通过，暂未发现异常"]')
        if element:
            return "check_have_rec_tag"
    except Exception as e:
        print(e)
        bb.result["msg"] = "发文助手检测未通过"
        return "failed"
    bb.result["msg"] = "发文助手检测未通过"
    return "failed"

def check_have_rec_tag():
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[4]/div[2]/div[1]')
        if element:
            return "input_post_title"
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
    driver.switch_to.alert.accept()
    return "failed"

def input_post_title():
    driver = bb[bb.browser + '_' + bb.appType]
    # title为空 不填
    if not bb.task['data'].get('title'):
        return "input_post_desc"

    title = bb.task['data']['title']

    try:
        element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div/div/input')
        if element:
            element.send_keys(title)
            return "input_post_desc"
    except Exception as e:
        print(e)
        bb.result["msg"] = "未检测到标题输入框或输入失败"
        return "failed"

    bb.result["msg"] = "未检测到标题输入框或输入失败"
    return "failed"

def input_post_desc():
    driver = bb[bb.browser + '_' + bb.appType]
    # desc为空 不填
    if not bb.task['data'].get('desc'):
        return "add_event"

    desc = bb.task['data']['desc']

    content_list = pyautoguiUtils.deal_content_to_list(desc)

    element = None
    try:
        # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[2]')
        element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[2]/div')
        if not element:
            bb.result["msg"] = "获取作品简介输入框失败"
            return "failed"
    except Exception as e:
        print(e)
        bb.result["msg"] = "获取作品简介输入框失败:\n" + str(e)
        return "failed"

    for content in content_list:
        try:
            element.send_keys(content)
            if content.startswith(('@', '#')):
                time.sleep(2)
                element.send_keys(Keys.ENTER)
                time.sleep(1)
        except Exception as e:
            print(e)
            bb.result["msg"] = "输入正文失败:\n" + str(e)
            return "task_failed"

    return "add_event"


#先跳过执行
def add_event():
    return "set_cover"
    if not bb.task['data'].get('addEvent') or not bb.task['data']['addEvent']:
        return "set_cover"

    if not pyautoguiUtils.check(os.path.join("dy", "add_event")):
        bb.result["msg"] = "未获取到作品活动奖励"
        return "failed"

    if pyautoguiUtils.click(os.path.join("dy", "add_event"), offset_y=40, sleep=2):
        return "set_cover"
    else:
        return "failed"


def set_cover():
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[5]/div/div[2]/div[1]/div/div[1]')
        if element:
            element.click()
            time.sleep(3)
            return "add_chapter"
    except Exception as e:
        print(e)
        bb.result["msg"] = "选择智能推荐封面失败：\n" + str(e)
        return "failed"

def add_chapter():
    return "add_location"


def add_location():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('location'):
        return "related_hot_spots"
    location = bb.task['data']['location']
    try:
        # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[8]/div[2]/div[2]/div/div')
        element = driver.find_element(By.XPATH, '//span[text()="输入地理位置"]')
        if element:
            element.click()
            time.sleep(1)
            element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[8]/div[2]/div[2]/div/div[1]/div[1]/div/div/input')
            time.sleep(0.5)
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(1)
            element.send_keys(location)
            time.sleep(5)
            try:
                element = driver.find_element(By.XPATH, '//div[text()="未搜索到相关位置"]')
                if element:
                    bb.result["msg"] = "未搜索到相关位置"
                    return "task_failed"
            except Exception as e:
                print(e)
            element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div/div/div/div[2]/div[1]/div[8]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div[1]')
            element.click()
            return "related_hot_spots"
    except Exception as e:
        print(e)
        bb.result["msg"] = "选择位置失败：\n" + str(e)
        return "failed"

    bb.result["msg"] = "选择位置失败"
    return "failed"

def related_hot_spots():
    # return "add_to_collection"
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('hotSpot'):
        return "add_to_collection"
    hotSpot = bb.task['data']['hotSpot']
    try:
        element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[10]/div[2]/div[1]')
        if element:
            element.click()
            time.sleep(1)
            element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[10]/div[2]/div[1]/div/div/input')
            time.sleep(0.5)
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(1)
            element.send_keys(hotSpot)
            time.sleep(5)
            try:
                element = driver.find_element(By.XPATH, '//div[text()="没有找到？换个词试试"]')
                if element:
                    bb.result["msg"] = "没有找到关联热点词，换个词试试"
                    return "task_failed"
            except Exception as e:
                print(e)
            # element = driver.find_element(By.XPATH, '/html/body/div[12]/div/div/div/div/div/div/div[2]')
            element = driver.find_element(By.XPATH, '//div[@class="semi-popover-content"]/div/div/div')
            element.click()
            return "add_to_collection"
    except Exception as e:
        print(e)
        bb.result["msg"] = "选择申请关联热点失败：\n" + str(e)
        return "failed"

    bb.result["msg"] = "选择申请关联热点失败"
    return "failed"


# 默认第一个合集
def add_to_collection():
    if not bb.task['data'].get('addToCollection') or not bb.task['data']['addToCollection']:
        return "sync_other_plat"
    #todo 同步到其他平台
    return "sync_other_plat"



def sync_other_plat():
    if not bb.task['data'].get('needSync2OtherPlat'):
        return "allow_save_video"
    #todo
    return "allow_save_video"


# 0 允许（默认） 1 不允许
def allow_save_video():
    driver = bb[bb.browser + '_' + bb.appType]
    # 不设置或者未0直接跳过 因为默认就是允许
    if not bb.task['data'].get('allow_save_video'):
        return "set_who_can_see"
    allow = bb.task['data']['allow_save_video']
    if allow == '0':
        return "set_who_can_see"
    elif allow == '1':
        try:
            element = driver.find_element(By.XPATH, '//span[text()="不允许"]/..')
            if element:
                element.click()
                return "set_who_can_see"
        except Exception as e:
            bb.result["msg"] = "允许他人保存视频设置失败:\n" + str(e)
            return "failed"
    else:
        bb.result["msg"] = "允许他人保存视频参数错误"
        return "task_failed"
    bb.result["msg"] = "设置允许他人保存视频失败"
    return "failed"


# 0 公开 1 好友可见 2 仅自己可见
def set_who_can_see():
    driver = bb[bb.browser + '_' + bb.appType]
    # 不设置或者未0直接跳过 因为默认就是公开
    if not bb.task['data'].get('who_can_see'):
        return "pub_time"
    who_can_see = bb.task['data']['who_can_see']
    if who_can_see == '0':
        return "pub_time"
    elif who_can_see == '1':
        try:
            element = driver.find_element(By.XPATH, '//span[text()="好友可见"]/..')
            if element:
                element.click()
                return "pub_time"
        except Exception as e:
            bb.result["msg"] = "点击好友可见按钮失败:\n" + str(e)
            return "failed"
    elif who_can_see == '2':
        try:
            element = driver.find_element(By.XPATH, '//span[text()="仅自己可见"]/..')
            if element:
                element.click()
                return "pub_time"
        except Exception as e:
            bb.result["msg"] = "点击仅自己可见按钮失败:\n" + str(e)
            return "failed"
    else:
        bb.result["msg"] = "设置谁可以看参数错误"
        return "task_failed"
    bb.result["msg"] = "设置谁可以看失败"
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
    if pubTime < nowTime + (2 * 60 * 60 + 5 * 60) or pubTime > nowTime + (14 * 24 * 60 * 60 - 5 * 60):
        bb.result["msg"] = "发布时间必须为至少两小时后，且小于十四天"
        return "task_failed"

    pubTime = float(pubTime)
    publishTime = time.strftime('%Y-%m-%d %H:%M', time.localtime(pubTime))

    try:
        # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[16]/div[1]/label[2]')
        element = driver.find_element(By.XPATH, '//span[text()="定时发布"]/..')
        if element:
            print(element)
            element.click()
            # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[14]/div[2]/div[2]/div[2]/div/div/div/input')
            # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[16]/div[2]/div[2]/div[2]/div/div/div/input')
            element = driver.find_element(By.XPATH, '//input[@placeholder="日期和时间"]')
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(0.5)
            element.send_keys(publishTime)
            time.sleep(0.5)
            element.send_keys(Keys.ENTER)
            return "pub"
    except Exception as e:
        print(e)
        bb.result["msg"] = "设置定时发布失败:\n" + str(e)
        return "failed"

    bb.result["msg"] = "设置定时发布失败"
    return "failed"


def pub():
    # return "task_success"
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        element = driver.find_element(By.XPATH, '//button[text()="发布"]')
        if element:
            element.click()
            time.sleep(3)
            return "check_pub"
    except Exception as e:
        bb.result["msg"] = "点击发布按钮失败:\n" + str(e)
        return "failed"
    bb.result["msg"] = "点击发布按钮失败"
    return "failed"

def check_pub():
    driver = bb[bb.browser + '_' + bb.appType]
    try:
        current_url = driver.current_url
        if current_url and current_url.endswith('content/manage'):
            return "task_success"
        else:
            bb.result["msg"] = "发布失败，可能出现手机验证码"
            return "failed"
    except Exception as e:
        bb.result["msg"] = "发布失败:\n" + str(e)
        return "failed"

def task_failed():
    close_browser()
    bb.result["code"] = -1
    return "success"


def task_success():
    close_browser()
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