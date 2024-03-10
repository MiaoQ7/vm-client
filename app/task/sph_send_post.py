import uuid
import time
from app.state.loop import bb, tt, fs
from app.libs import ihttp
from loguru import logger
from app.utils import ip_utils, browser_utils
import app.libs.pyautoguiUtils as pyautoguiUtils
import os
from app.utils import ip_utils, browser_utils, proxy_utils, win_utils, selenium_utils
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
        driver.get("https://channels.weixin.qq.com/platform/post/create")
        return "upload_video"


def upload_video():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('video'):
        bb.result["msg"] = "获取视频失败"
        return "task_failed"

    filepath = bb.task['data']['video']
    whole_path = os.path.join(bb.config.resBak, filepath)
    # print("----" + whole_path)
    logger.info("shpsend_post:upload_video  whole_path - {}", whole_path)
    try:
        element = driver.find_element(By.XPATH, '//input[@type="file"]')
        if element:
            print(element)
            element.send_keys(whole_path)
            return "wait_upload_video"
    except Exception as e:
        print(e)
        logger.exception("上传视频失败 {}", e)
        bb.result["msg"] = "上传视频失败,error "
        return "task_failed"
    bb.result["msg"] = "上传视频失败"
    return "failed"

def wait_upload_video():
    driver = bb[bb.browser + '_' + bb.appType]
    # try:
    #     element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div/div[1]/div/div[1]')
    #     if not element:
    #         driver.refresh()
    #         return "upload_video"
    # except Exception as e:
    #     driver.refresh()
    #     return "upload_video"
    try:
        element = driver.find_element(By.XPATH, '//video[@id="fullScreenVideo"]')
        if element:
            return "input_post_desc"
    except Exception as e:
        print(e)
        bb.result["msg"] = "视频上传失败"
        return "failed"
    bb.result["msg"] = "视频上传失败"
    return "failed"


def input_post_desc():
    driver = bb[bb.browser + '_' + bb.appType]
    # desc为空 不填
    if not bb.task['data'].get('desc'):
        return "add_location"

    desc = bb.task['data']['desc']

    # content_list = pyautoguiUtils.deal_content_to_list(desc)

    element = None
    try:
        element = driver.find_element(By.XPATH, '//div[@class="input-editor"]')
        if not element:
            bb.result["msg"] = "获取视频描述输入框失败"
            return "failed"
    except Exception as e:
        print(e)
        bb.result["msg"] = "获取视频描述输入框失败:\n" + str(e)
        return "failed"

    try:
        element.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.5)
        element.send_keys(desc)
    except Exception as e:
        print(e)
        bb.result["msg"] = "输入视频描述失败:\n" + str(e)
        return "task_failed"
    # for content in content_list:
    #     try:
    #         element.send_keys(content)
    #         if content.startswith(('@', '#')):
    #             time.sleep(2)
    #             element.send_keys(Keys.ENTER)
    #             time.sleep(1)
    #     except Exception as e:
    #         print(e)
    #         bb.result["msg"] = "输入正文失败:\n" + str(e)
    #         return "task_failed"

    return "add_location"


def add_location():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('location'):
        return "add_to_collection"
    location = bb.task['data']['location']
    try:
        element = driver.find_element(By.XPATH, '//div[@class="position-display"]')
        if element:
            element.click()
        else:
            bb.result["msg"] = "选择位置失败"
            return "failed"
        time.sleep(1)
        element = driver.find_element(By.XPATH, '//input[@placeholder="搜索附近位置"]')
        time.sleep(1)
        if element:
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(0.5)
            element.send_keys(location)
        else:
            bb.result["msg"] = "选择位置失败"
            return "failed"
        time.sleep(3)
        elements = driver.find_elements(By.XPATH, '//div[@class="location-item"]')
        if elements and len(elements) > 2 and elements[1]:
            elements[1].click()
            return "add_to_collection"
    except Exception as e:
        logger.error("选择位置失败 {}", e)
        bb.result["msg"] = "选择位置失败：\n" + str(e)
        return "failed"

    bb.result["msg"] = "选择位置失败"
    return "failed"


# 默认第一个合集
def add_to_collection():
    driver = bb[bb.browser + '_' + bb.appType]
    # logger.info("dysend_post:upload_video  whole_path - {}", whole_path)
    if not bb.task['data'].get('addToCollection') or not bb.task['data']['addToCollection']:
        return "add_link"
    try:
        element = driver.find_element(By.XPATH, '//div[text()="选择合集"]')
        if element:
            element.click()
            time.sleep(1)
            elements = driver.find_elements(By.XPATH, '//div[@class="post-album-wrap"]/div[2]/div')
            # 有合集
            logger.info("sph_send_post:add_to_collection count - {}", len(elements))
            if elements and len(elements) == 3:
                # print("选择合集")
                elements = driver.find_elements(By.XPATH, '//div[@class="post-album-wrap"]/div[2]/div[2]/div')
                if elements and len(elements) > 0:
                    element = elements[0]
                    element.click()
                    return "add_link"
                    # 选择第一个
            else:
                # 需要创建合集
                # print("需要创建合集")
                bb.result["msg"] = "添加合集失败，合集数量为零，请手动创建合集（也有可能是获取浏览器元素失败）"
                return "task_failed"
    except Exception as e:
        logger.exception("添加合集失败 {}", e)
        bb.result["msg"] = "添加合集失败，合集数量为零，请手动创建合集"
        return "failed"
    bb.result["msg"] = "添加合集失败"
    return "failed"


# sph_link 0 不需要  1 公众号文章  2 红包封面  3 表情
def add_link():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('sph_add_link'):
        return "attend_event"
    sph_link = bb.task['data']['sph_add_link']
    if sph_link != '0' and (not bb.task['data'].get('sph_link') or not bb.task['data']['sph_link']):
        bb.result["msg"] = "添加链接失败，请输入需要添加的链接"
        return "task_failed"
    link = bb.task['data']['sph_link']

    xpath_str = None
    if sph_link == '0':
        return "attend_event"
    elif sph_link == '1':
        xpath_str = '//div[@class="link-list-options"]/div[1]'
    elif sph_link == '2':
        xpath_str = '//div[@class="link-list-options"]/div[2]'
    elif sph_link == '3':
        xpath_str = '//div[@class="link-list-options"]/div[3]'
    else:
        bb.result["msg"] = "添加链接失败，添加链接参数错误"
        return "task_failed"

    try:
        element = driver.find_element(By.XPATH, '//div[@class="link-display-wrap"]')
        if element:
            element.click()
            time.sleep(1)
            element = driver.find_element(By.XPATH, xpath_str)
            if element:
                element.click()
                time.sleep(1)
                element = driver.find_element(By.XPATH, '//div[@class="link-input-wrap"]//input[@type="text"]')
                if element:
                    logger.info("{} sph_send_post:add_link choose type - {}", bb.task['taskId'], element.text)
                    element.send_keys(Keys.CONTROL, 'a')
                    time.sleep(0.5)
                    element.send_keys(link)
                    time.sleep(1)
                    try:
                        element = driver.find_element(By.XPATH, '//div[@class="link-input-wrap"]/div[@class="error-link"]')
                        if element:
                            logger.info("{} sph_send_post:add_link choose type - 链接上传失败 链接不符合要求，官方提示", bb.task['taskId'])
                            bb.result["msg"] = "添加链接失败，链接不符合要求，官方提示"
                            return "task_failed"
                        else:
                            return "attend_event"
                    except Exception:
                        return "attend_event"
    except Exception as e:
        logger.error("{} 添加链接失败 {}", bb.task['taskId'], e)
        bb.result["msg"] = "添加链接失败，操作浏览器元素失败:\n" + str(e)
        return "failed"

    bb.result["msg"] = "添加链接失败，操作浏览器元素失败"
    return "failed"

def attend_event():
    driver = bb[bb.browser + '_' + bb.appType]
    if not bb.task['data'].get('addEvent') or not bb.task['data']['addEvent']:
        return "pub_time"
    if not bb.task['data'].get('event') or not bb.task['data']['event']:
        bb.result["msg"] = "参加活动，但没有录入活动信息"
        return "task_failed"

    event = bb.task['data']['event']


    element = selenium_utils.find_element(driver=driver, param='//div[@class="activity-display-wrap"]')
    # element = driver.find_element(By.XPATH, '//div[@class="activity-display-wrap"]')
    if element:
        element.click()
        time.sleep(1)
        # element = driver.find_element(By.XPATH, '//div[@class="activity-filter-wrap"]//input[@type="text"]')
        element = selenium_utils.find_element(driver=driver, param='//div[@class="activity-filter-wrap"]//input[@type="text"]')
        if element:
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(0.5)
            element.send_keys(event)
            time.sleep(2)
            # element = driver.find_element(By.XPATH, '//div[@class="activity-filter-wrap"]/div[@class="common-option-list-wrap"]/div[2]')
            element = selenium_utils.find_element(driver=driver, param='//div[@class="activity-filter-wrap"]/div[@class="common-option-list-wrap"]/div[2]')
            if element:
                element.click()
                return "pub_time"

    bb.result["msg"] = "参加活动失败"
    return "failed"


def _selectYear(driver, year):
    years = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[2]/table/tbody/tr/td/a')
    for y in years:
        if y.text == year:
            y.click()

def _selectMonth(driver, month):
    months = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[2]/table/tbody/tr/td/a')
    for m in months:
        if m.text == month:
            m.click()

def _selectDay(driver, day):
    days = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[2]/table/tbody/tr/td/a')
    for d in days:
        if d.text == day:
            d.click()

def _inputTime(driver, time):
    # /html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[3]/dl/dt/span/div/span/input
    ele = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[3]/dl/dt/span/div/span/input')
    ele.send_keys(Keys.CONTROL,'a')
    ele.send_keys(time)

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
    # publishTime = time.strftime('%Y-%m-%d %H:%M', time.localtime(pubTime))
    local_time = time.localtime(pubTime)
    year = local_time.tm_year
    month = local_time.tm_mon
    day = local_time.tm_mday
    hour = local_time.tm_hour
    min = local_time.tm_min


    try:
        # element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[16]/div[1]/label[2]')
        element = driver.find_element(By.XPATH, '//*[@id="container-wrap"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[1]/div[2]/div/label[2]/span')
        if element:
            element.click()
            input = driver.find_element(By.XPATH, '//*[@id="container-wrap"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dt/span[1]/div/span/input')
            if input:
                input.click()
                _selectYear(driver, str(year))
                _selectMonth(driver, str(month))
                _selectDay(driver, str(day))
                _inputTime(driver, str(hour) + ':' + str(min))
                element.click()
                return "input_post_title"
    except Exception as e:
        print(e)
        bb.result["msg"] = "设置定时发布失败:\n" + str(e)
        return "failed"

    bb.result["msg"] = "设置定时发布失败"
    return "failed"

def input_post_title():
    if not bb.task['data'].get('title'):
        return "pub"

    title = bb.task['data']['title']

    if len(title) < 6:
        bb.result["msg"] = "短标题至少6个字"
        return "task_failed"


    driver = bb[bb.browser + '_' + bb.appType]
    element = selenium_utils.find_element(driver=driver, param='//div[@class="post-short-title-wrap"]//input[@type="text"]')
    if element:
        element.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.5)
        element.send_keys(title)
        return "pub"
    else:
        bb.result["msg"] = "输入短标题失败"
        return "failed"


def pub():
    # return "task_success"
    driver = bb[bb.browser + '_' + bb.appType]
    element = selenium_utils.find_element(driver=driver, param='//div[@class="form-btns"]//button[@type="button" and text()="发表"]')
    if element:
        element.click()
        time.sleep(3)
        # print(element.text)
        return "task_success"
    bb.result["msg"] = "点击发布按钮失败"
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