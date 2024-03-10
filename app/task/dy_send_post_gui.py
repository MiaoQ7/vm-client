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
    if res == 'timeout':
        bb.result["msg"] = "打开浏览器超时"
        return "task_failed"
    if res == 'failed':
        bb.result["msg"] = "打开浏览器失败"
        return "task_failed"
    if res == 'success':
        return "enter_creator"


def enter_creator():
    if pyautoguiUtils.check(os.path.join("dy", "tougao")):
        if pyautoguiUtils.click(os.path.join("dy", "tougao")):
            bb.result["msg"] = "点击投稿进入创作者中心"
            return "upload_video"
    bb.result["msg"] = "点击投稿进入创作者中心失败"
    return "failed"


def upload_video():
    if pyautoguiUtils.check(os.path.join("dy", "upload_video_btn")):
        if pyautoguiUtils.click(os.path.join("dy", "upload_video_btn")):
            time.sleep(3)
            bb.result["msg"] = "点击上传视频按钮成功"
            return "input_upload_video_file_path"
    bb.result["msg"] = "点击上传视频按钮失败"
    return "failed"


def input_upload_video_file_path():
    filepath = None
    if not bb.task['data'].get('video'):
        bb.result["msg"] = "获取视频失败"
        return "task_failed"
    filepath = bb.task['data']['video']
    whole_path = os.path.join(bb.config.resBak, filepath)
    dir_path = os.path.dirname(whole_path)
    if pyautoguiUtils.check(os.path.join("system", "system_file_return_and_forward")):
        if pyautoguiUtils.click(os.path.join("system", "system_file_refresh1"), -150, 0, 2):
            # file_path = "D:\\video"
            pyautoguiUtils.input_with_clipboard(dir_path, True)
            bb.result["msg"] = "资源管理器输入文件夹地址成功"
            return "input_upload_video_file_name"
    bb.result["msg"] = "资源管理器输入文件夹地址失败"
    return "failed"

def input_upload_video_file_name():
    file_name = None
    if not bb.task['data'].get('video'):
        bb.result["msg"] = "获取视频失败"
        return "task_failed"
    filepath = bb.task['data']['video']
    whole_path = os.path.join(bb.config.resBak, filepath)
    file_name = os.path.basename(whole_path)
    if pyautoguiUtils.check(os.path.join("system", "system_file_filename_input")):
        if pyautoguiUtils.click(os.path.join("system", "system_file_filename_input"), sleep=2):
            # file_name = "1.mp4"
            pyautoguiUtils.input_with_clipboard(file_name)
            pyautoguiUtils.click(os.path.join("system", "system_file_open_button"))
            if pyautoguiUtils.check(os.path.join("system", 'system_file_open_error')):
                bb.result["msg"] = "上传视频文件未找到"
                return "task_failed"
            bb.result["msg"] = "资源管理器选择视频成功"
            return "wait_upload_video"
    bb.result["msg"] = "资源管理器选择视频失败"
    return "failed"


def wait_upload_video():
    if pyautoguiUtils.check(os.path.join("dy", "review_video")):
        return "input_post_title"
    bb.result["msg"] = "视频还未上传成功"
    return "failed"


def input_post_title():
    # title为空 不填
    if not bb.task['data'].get('title'):
        return "input_post_desc"

    title = bb.task['data']['title']
    if not pyautoguiUtils.check(os.path.join("dy", "review_video")):
        bb.result["msg"] = "视频还未上传成功"
        return "failed"
    if not pyautoguiUtils.check(os.path.join("dy", "title_input")):
        bb.result["msg"] = "未获取到标题输入框"
        return "failed"
    if pyautoguiUtils.click(os.path.join("dy", "title_input")):
        if pyautoguiUtils.input_with_clipboard(title):
            return "input_post_desc"
        else:
            return "failed"
    else:
        return "failed"


def input_post_desc():
    # desc为空 不填
    if not bb.task['data'].get('desc'):
        return "add_event"

    desc = bb.task['data']['desc']
    if not pyautoguiUtils.check(os.path.join("dy", "desc_input")):
        bb.result["msg"] = "未获取到描述输入框"
        return "failed"

    if pyautoguiUtils.check(os.path.join("dy", "desc_input")):
        # 点击正文输入框
        if pyautoguiUtils.click(os.path.join("dy", "desc_input"), sleep=2):
            content_list = pyautoguiUtils.deal_content_to_list(desc)
            if pyautoguiUtils.input_words_with_clipboard(content_list):
                return 'add_event'
    bb.result["msg"] = "输入视频描述失败"
    return "task_failed"


def add_post_topic():
    # labels为空 不填
    if not bb.task['data'].get('labels'):
        return "desc_at_friend"

    topics = bb.task['data']['labels']
    if not topics or len(topics) == 0:
        return "desc_at_friend"
    if not pyautoguiUtils.check(os.path.join("dy", "add_post_topic")):
        bb.result["msg"] = "未获取到添加话题按钮"
        return "failed"

    try:
        for topic in topics:
            if pyautoguiUtils.click(os.path.join("dy", "add_post_topic")):
                pyautoguiUtils.input_with_clipboard(topic, inputEnter=True)
            else:
                continue
    except:
        bb.result["msg"] = "添加话题失败"
        return 'task_failed'
    return "desc_at_friend"


def desc_at_friend():
    # friend为空 不填
    if not bb.task['data'].get('atUsers'):
        return "add_event"

    friends = bb.task['data']['atUsers']
    if not friends or len(friends) == 0:
        return "add_event"
    if not pyautoguiUtils.check(os.path.join("dy", "at_friend")):
        bb.result["msg"] = "未获取到at好友按钮"
        return "failed"

    try:
        for friend in friends:
            if pyautoguiUtils.click(os.path.join("dy", "at_friend")):
                pyautoguiUtils.input_with_clipboard(friend, inputEnter=True, sleep=3)
            else:
                continue
    except:
        bb.result["msg"] = "at好友失败"
        return 'task_failed'
    return "add_event"


#默认参加第一个
def add_event():
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
    if not pyautoguiUtils.check(os.path.join("dy", "set_cover")):
        bb.result["msg"] = "未获取到设置封面位置"
        return "failed"

    if pyautoguiUtils.click(os.path.join("dy", "set_cover"), offset_y=50, sleep=5):
        if pyautoguiUtils.check(os.path.join("dy", "select_cover_title")) and pyautoguiUtils.check(os.path.join("dy", "select_cover_finish")):
            if pyautoguiUtils.click(os.path.join("dy", "select_cover_finish"), sleep=2):
                return "add_chapter"
            else:
                bb.result["msg"] = "设置封面失败-点击完成失败"
                return "task_failed"
        else:
            bb.result["msg"] = "设置封面失败-在设置封面页面获取元素失败"
            return "task_failed"
    else:
        return "failed"


def add_chapter():
    return "before_add_location_scroll_down"


def before_add_location_scroll_down():
    if pyautoguiUtils.scrollDown():
        return "check_already_open_sync"
    else:
        bb.result["msg"] = "浏览器滚动到底部失败"
        return "task_failed"


def check_already_open_sync():
    if not pyautoguiUtils.check(os.path.join("dy", "sync_2_other_plat_switch_open")):
        return "add_location"

    if pyautoguiUtils.click(os.path.join("dy", "sync_2_other_plat_switch_open")):
        pyautoguiUtils.scrollDown()
        return "add_location"
    else:
        bb.result["msg"] = "开启同步到其他平台失败-already"
        return "task_failed"


def add_location():
    if not bb.task['data'].get('location'):
        return "related_hot_spots"
    location = bb.task['data']['location']
    if not pyautoguiUtils.check(os.path.join("dy", "add_title")) or not pyautoguiUtils.check(os.path.join("dy", "input_location")):
        bb.result["msg"] = "未获取到设置位置入口"
        return "failed"
    x, y = pyautoguiUtils.center(os.path.join("dy", "input_location"))
    if pyautoguiUtils.click(os.path.join("dy", "input_location")):
        if pyautoguiUtils.input_with_clipboard(location):
            for i in range(5):
                if not pyautoguiUtils.check(os.path.join("dy", "search_location_error")):
                    time.sleep(1)
                    continue
                else:
                    bb.result["msg"] = "搜索地点不存在或失败"
                    return "task_failed"
            # pyautoguiUtils.press_hotkey('enter')
            pyautoguiUtils.clickWithXY(x, y, 0, 40, sleep=1)
            return "related_hot_spots"
    else:
        return "failed"


def related_hot_spots():
    if not bb.task['data'].get('hotSpot'):
        return "add_to_collection"
    hotSpot = bb.task['data']['hotSpot']
    if not pyautoguiUtils.check(os.path.join("dy", "input_hot_spots")):
        bb.result["msg"] = "未获取到关联热点词入口"
        return "failed"
    x, y = pyautoguiUtils.center(os.path.join("dy", "input_hot_spots"))
    if pyautoguiUtils.click(os.path.join("dy", "input_hot_spots")):
        if pyautoguiUtils.input_with_clipboard(hotSpot):
            for i in range(5):
                if not pyautoguiUtils.check(os.path.join("dy", "not_found_hot_spots")):
                    time.sleep(1)
                    continue
                else:
                    bb.result["msg"] = "搜索热点词不存在或失败"
                    return "task_failed"
            # pyautoguiUtils.press_hotkey('enter')
            pyautoguiUtils.clickWithXY(x, y, 0, 40, sleep=1)
            return "add_to_collection"
    else:
        return "failed"


# 默认第一个合集
def add_to_collection():
    if not bb.task['data'].get('addToCollection') or not bb.task['data']['addToCollection']:
        return "sync_other_plat"
    if not pyautoguiUtils.check(os.path.join("dy", "select_collection")):
        bb.result["msg"] = "未获取到选择合集入口"
        return "failed"
    if pyautoguiUtils.click(os.path.join("dy", "select_collection")):
        if pyautoguiUtils.check(os.path.join("dy", "not_found_collection")):
            if pyautoguiUtils.click(os.path.join("dy", "not_found_collection"), offset_y=40):
                pyautoguiUtils.scrollDown()
                return "sync_other_plat"
            else:
                bb.result["msg"] = "点击第一个合集失败"
                return "task_failed"
        else:
            bb.result["msg"] = "未获取到选择合集下拉列表"
            return "task_failed"
    else:
        return "failed"



def sync_other_plat():
    if not bb.task['data'].get('needSync2OtherPlat'):
        return "allow_save_video"

    if not pyautoguiUtils.check(os.path.join("dy", "sync_2_other_plat")):
        bb.result["msg"] = "未获取到同步其他平台入口"
        return "failed"

    region = None
    region = pyautoguiUtils.locateOnScreen(os.path.join("dy", "sync_2_other_plat"))
    if not region:
        bb.result["msg"] = "获取到同步其他平台开关窗口失败"
        return "failed"

    if pyautoguiUtils.check_with_region(os.path.join("dy", "sync_2_other_plat_switch"), region):
        if pyautoguiUtils.click_with_region(os.path.join("dy", "sync_2_other_plat_switch"), region):
            pyautoguiUtils.scrollDown()
            return "input_other_plat_title"
        else:
            bb.result["msg"] = "开启同步到其他平台失败"
            return "task_failed"
    else:
        bb.result["msg"] = "获取同步到其他平台开关失败"
        return "task_failed"



def input_other_plat_title():
    return "allow_save_video"
    # title = None
    # if bb.task['data'].get('otherPlatTitle'):
    #     title = bb.task['data']['otherPlatTitle']
    # if not title:
    #     return "allow_save_video"
    # if len(title) > 30:
    #     bb.result["msg"] = "输入其他平台视频标题错误-标题过长"
    #     return "task_failed"
    #
    # if not pyautoguiUtils.check(os.path.join("dy", "input_other_plat_title")):
    #     bb.result["msg"] = "未获取到输入其他平台标题入口"
    #     return "failed"
    #
    # if pyautoguiUtils.click(os.path.join("dy", "input_other_plat_title"), sleep=5):
    #     if pyautoguiUtils.check(os.path.join("dy", "input_xigua_title")):
    #         if pyautoguiUtils.click(os.path.join("dy", "input_xigua_title"), sleep=2):
    #             if pyautoguiUtils.input_with_clipboard(title):
    #                 if pyautoguiUtils.check(os.path.join("dy", "input_xigua_title_success_btn")):
    #                     if pyautoguiUtils.click(os.path.join("dy", "input_xigua_title_success_btn")):
    #                         return "allow_save_video"
    #                     else:
    #                         bb.result["msg"] = "输入西瓜视频标题失败-输入后点击成功按钮失败"
    #                         return "task_failed"
    #                 else:
    #                     bb.result["msg"] = "输入西瓜视频标题失败-输入后点击成功按钮失败"
    #                     return "task_failed"
    #             else:
    #                 bb.result["msg"] = "输入西瓜视频标题失败-输入失败"
    #                 return "task_failed"
    #         else:
    #             bb.result["msg"] = "输入西瓜视频标题失败-点击输入框失败"
    #             return "task_failed"
    #     else:
    #         bb.result["msg"] = "输入西瓜视频标题失败-未获取到输入框为止"
    #         return "task_failed"
    # else:
    #     return "failed"


# 0 允许（默认） 1 不允许
def allow_save_video():
    # 不设置或者未0直接跳过 因为默认就是允许
    if not bb.task['data'].get('allow_save_video'):
        return "set_who_can_see"
    allow = bb.task['data']['allow_save_video']
    if allow == '0':
        return "set_who_can_see"
    elif allow == '1':
        if pyautoguiUtils.check(os.path.join("dy", "not_allow_save_video")):
            if pyautoguiUtils.click(os.path.join("dy", "not_allow_save_video")):
                return "set_who_can_see"
            else:
                bb.result["msg"] = "点击不允许保存视频按钮失败"
                return "failed"
        else:
            bb.result["msg"] = "获取不允许保存视频按钮失败"
            return "failed"
    else:
        bb.result["msg"] = "允许他人保存视频参数错误"
        return "task_failed"


# 0 公开 1 好友可见 2 仅自己可见
def set_who_can_see():
    # 不设置或者未0直接跳过 因为默认就是公开
    if not bb.task['data'].get('who_can_see'):
        return "pub_time"
    who_can_see = bb.task['data']['who_can_see']
    if who_can_see == '0':
        return "pub_time"
    elif who_can_see == '1':
        if pyautoguiUtils.check(os.path.join("dy", "friend_can_see")):
            if pyautoguiUtils.click(os.path.join("dy", "friend_can_see")):
                pyautoguiUtils.scrollDown()
                return "pub_time"
            else:
                bb.result["msg"] = "点击好友可见按钮失败"
                return "failed"
        else:
            bb.result["msg"] = "获取好友可见按钮失败"
            return "failed"
    elif who_can_see == '2':
        if pyautoguiUtils.check(os.path.join("dy", "only_self_can_see")):
            if pyautoguiUtils.click(os.path.join("dy", "only_self_can_see")):
                pyautoguiUtils.scrollDown()
                return "pub_time"
            else:
                bb.result["msg"] = "点击仅自己可见按钮失败"
                return "failed"
        else:
            bb.result["msg"] = "获取仅自己可见按钮失败"
            return "failed"
    else:
        bb.result["msg"] = "设置谁可以看参数错误"
        return "task_failed"


def pub_time():
    # 10位时间戳
    if not bb.task['data'].get('pub_time'):
        return "pub"
    pubTime = bb.task['data'].get('pub_time')
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
    if pyautoguiUtils.check(os.path.join("dy", "set_pub_time")):
        if pyautoguiUtils.click(os.path.join("dy", "set_pub_time")):
            if pyautoguiUtils.check(os.path.join("dy", "set_pub_time_icon")):
                if pyautoguiUtils.click(os.path.join("dy", "set_pub_time_icon")):
                    pyautoguiUtils.press_hotkey_mult("Ctrl", "a")
                    if pyautoguiUtils.input_with_clipboard(publishTime):
                        pyautoguiUtils.scrollDown()
                        return "pub"
                    else:
                        bb.result["msg"] = "输入时间失败"
                        return "task_failed"
                else:
                    bb.result["msg"] = "点击时间设置图标失败"
                    return "task_failed"
            else:
                bb.result["msg"] = "查找时间设置图标失败"
                return "task_failed"
        else:
            bb.result["msg"] = "点击定时发布按钮失败"
            return "failed"
    else:
        bb.result["msg"] = "获取定时发布按钮失败"
        return "failed"


def pub():
    # return "task_success"
    if pyautoguiUtils.check(os.path.join("dy", "pub")):
        if pyautoguiUtils.click(os.path.join("dy", "pub")):
            for i in range(15):
                if not pyautoguiUtils.check(os.path.join("dy", "pub_phone_check")):
                    continue
                else:
                    bb.result["msg"] = "发布出现手机号码验证"
                    return "task_failed"
            return "task_success"
        else:
            bb.result["msg"] = "点击发布按钮失败"
            return "failed"
    else:
        bb.result["msg"] = "获取发布按钮失败"
        return "failed"

def task_failed():
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
