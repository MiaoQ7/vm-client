import time

import names
import os
from loguru import logger

from app.libs import ihttp
from app.sms import ismsManager
from app.state.loop import bb, tt
from app.utils import ip_utils
import app.libs.pyautoguiUtils as pyautoguiUtils


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
    return "send_post"


def send_post():
    if pyautoguiUtils.check(os.path.join("xhs", "home_send_post")):
        if pyautoguiUtils.click(os.path.join("xhs", "home_send_post")):
            return "upload_video"
    bb.result["msg"] = "点击发布笔记失败"
    return "task_failed"


def upload_video():
    if pyautoguiUtils.check(os.path.join('xhs', 'upload_sms_login_title')):
        # 可能会丢失登录态，尝试刷新一下
        pyautoguiUtils.press_hotkey()
        pyautoguiUtils.press_hotkey()
        return "upload_video"
    if pyautoguiUtils.check(os.path.join("xhs", "upload_video_button")):
        if pyautoguiUtils.click(os.path.join("xhs", "upload_video_button")):
            time.sleep(3)
            return "input_upload_video_file_path"
    bb.result["msg"] = "点击上传视频按钮失败"
    return "task_failed"


def input_upload_video_file_path():
    try:
        filepath = bb.task['data']['video']
    except:
        bb.result["msg"] = "输入视频路径失败:缺少视频路径"
        return "task_failed"
    whole_path = os.path.join(bb.config.resBak, filepath)
    dir_path = os.path.dirname(whole_path)
    if pyautoguiUtils.check(os.path.join("system", "system_file_return_and_forward")):
        if pyautoguiUtils.click(os.path.join("system", "system_file_refresh"), -50, 0, 2):
            pyautoguiUtils.input_with_clipboard(dir_path, True)
            return "input_upload_video_file_name"
    bb.result["msg"] = "点击上传视频按钮失败"
    return "task_failed"


def input_upload_video_file_name():
    try:
        filepath = bb.task['data']['video']
    except:
        bb.result["msg"] = "输入视频名失败:缺少视频路径"
        return "task_failed"
    whole_path = os.path.join(r"E:\root\project\resBak", filepath)
    file_name = os.path.basename(whole_path)
    if pyautoguiUtils.check(os.path.join("system", "system_file_filename_input")):
        if pyautoguiUtils.click(os.path.join("system", "system_file_filename_input"), sleep=2):
            pyautoguiUtils.input_with_clipboard(file_name)
            pyautoguiUtils.click(os.path.join("system", "system_file_open_button"))
            if pyautoguiUtils.check(os.path.join("system", 'system_file_open_error')):
                bb.result["msg"] = "上传视频文件未找到"
                return "task_failed"
            return "start_upload_video"
    bb.result["msg"] = "点击上传视频按钮失败"
    return "task_failed"


def start_upload_video():
    if pyautoguiUtils.check(os.path.join("xhs", "evaluate_send_post_title")):
        pyautoguiUtils.click(os.path.join("xhs", "ignore_evaluate_send_post"), sleep=1)
    if pyautoguiUtils.check(os.path.join("xhs", "upload_video_detail_button")) or pyautoguiUtils.check(
            os.path.join("xhs", "cancel_upload_video")):
        return 'wait_upload_video'
    if pyautoguiUtils.check(os.path.join("system", "system_file_open_button")):
        pyautoguiUtils.click(os.path.join("system", "system_file_open_button"), sleep=2)
    time.sleep(5)
    bb.result["msg"] = "开始上传视频失败"
    return "task_failed"


def wait_upload_video():
    wait_count = 0
    max_wait_count = 10
    while wait_count < max_wait_count:
        time.sleep(5)
        if pyautoguiUtils.check(os.path.join("xhs", "upload_video_detail_button")):
            return 'input_post_title'
    bb.result["msg"] = "上传视频超时"
    return "task_failed"


def input_post_title():
    try:
        title = bb.task['data']['title']
    except:
        return 'input_post_desc'

    # TODO:可能是空的
    if pyautoguiUtils.check(os.path.join("xhs", "title_input")):
        # 点击标题输入框
        if pyautoguiUtils.click(os.path.join("xhs", "title_input"), sleep=2):
            if pyautoguiUtils.input_with_clipboard(title):
                return 'input_post_desc'
    bb.result["msg"] = "输入视频标题失败"
    return "task_failed"


def input_post_desc():
    try:
        desc = bb.task['data']['desc']
    except:
        return 'input_post_desc'
    if pyautoguiUtils.check(os.path.join("xhs", "desc_input")):
        # 点击正文输入框
        if pyautoguiUtils.click(os.path.join("xhs", "desc_input"), sleep=2):
            content_list = pyautoguiUtils.deal_content_to_list(desc)
            if pyautoguiUtils.input_words_with_clipboard(content_list):
                return 'to_send_post'
    bb.result["msg"] = "输入视频正文失败"
    return "task_failed"


def add_location():
    return "to_send_post"
    # # 判断添加位置是否存在
    # if pyautoguiUtils.check(os.path.join("xhs", "add_location")):
    #     # 点击添加位置
    #     if pyautoguiUtils.click(os.path.join("xhs", "add_location"), sleep=2):
    #         location = "美国香港"
    #         if pyautoguiUtils.input_with_clipboard(location):
    #             if pyautoguiUtils.check(os.path.join("xhs", "add_location_loading")) or pyautoguiUtils.check(
    #                     os.path.join("xhs", "no_match_location")):
    #                 time.sleep(3)
    #             if pyautoguiUtils.check(os.path.join("xhs", "add_location_loading")) or pyautoguiUtils.check(
    #                     os.path.join("xhs", "no_match_location")):
    #                 bb.result["msg"] = "位置不存在或者位置加载失败"
    #                 return "task_failed"
    #             if pyautoguiUtils.check(os.path.join("xhs", "add_location_title")):
    #                 pyautoguiUtils.click(os.path.join("xhs", "add_location_title"), 200, 50, 1)
    #                 if not pyautoguiUtils.check(os.path.join("xhs", "add_location")):
    #                     return "to_send_post"
    #             bb.result["msg"] = "选择位置出错"
    #             return "task_failed"
    # bb.result["msg"] = "添加位置失败"
    # return "task_failed"


def to_send_post():
    if pyautoguiUtils.check(os.path.join("xhs", "send_post_button")):
        # 点击发布按钮
        if pyautoguiUtils.click(os.path.join("xhs", "send_post_button"), sleep=2):
            return 'check_send_post'
    bb.result["msg"] = "点击发布视频按钮失败"
    return "task_failed"


def check_send_post():
    if pyautoguiUtils.check(os.path.join("xhs", "send_post_success")):
        # 点击发布按钮
        if pyautoguiUtils.click(os.path.join("xhs", "send_post_success"), sleep=2):
            bb.result["msg"] = "上传视频成功"
            return 'task_success'
    bb.result["msg"] = "检查发布视频失败"
    return "task_failed"


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
    return "failed"


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
