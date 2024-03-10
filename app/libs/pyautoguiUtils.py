import os
import sys
import time
from loguru import logger
import pyautogui
import pyperclip
import re

_debug_ = False

_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_project_path = os.path.dirname(_parent_dir)
_exe_directory = _project_path
# 如果_exe_directory包含_MEIPASS,代表是打包成exe后执行,需要修改执行目录路径
if "_MEI" in _exe_directory:
    # 获取可执行文件所在的目录
    _exe_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 打包后关闭debug
    _debug_ = False

# 位置截图文件路径
_screenshots_dir = os.path.join(_project_path, "screenshots")


# 获取截图路径
def spath(screenshot_name):
    return os.path.join(_screenshots_dir, screenshot_name + ".png")


# 查找截图位置
def locateOnScreen(screenshot_name):
    logger.info(f"locateOnScreen {screenshot_name}")
    time.sleep(1)
    return pyautogui.locateOnScreen(spath(screenshot_name), confidence=0.85)


def hook_click(info, x, y):
    logger.info("%s click: %s, %s" % (info, x, y))
    pyautogui.click(x, y)


def check(screenshot_name):
    try:
        x, y = center(screenshot_name)
        return True
    except Exception as e:
        logger.error("%s check error: %s" % (screenshot_name, e))
        if _debug_:
            screenshot(screenshot_name + "_check_error")
    finally:
        pass
    return False


def click(screenshot_name, offset_x=0, offset_y=0, sleep=0.1):
    try:
        x, y = center(screenshot_name)
        x = x + offset_x
        y = y + offset_y
        pyautogui.click(x, y)
        logger.info(" %s click: %s, %s" % (screenshot_name, x, y))
        time.sleep(sleep)
        return True
    except Exception as e:
        logger.error("%s click error: %s" % (screenshot_name, e))
        if _debug_:
            screenshot(screenshot_name + "_click_error")
    finally:
        pass
    return False


# 用pyautogui查找截图位置
def center(screenshot_name):
    x, y = pyautogui.center(locateOnScreen(screenshot_name))
    logger.info("%s center: %s, %s" % (screenshot_name, x, y))
    return x, y


# 截取屏幕
def screenshot(name):
    time.sleep(5)

    # 获取屏幕的大小
    screen_width, screen_height = pyautogui.size()
    # 截屏整个屏幕
    screenshot = pyautogui.screenshot()
    # 保存截屏图片
    screenshot.save(os.path.join(_screenshots_dir, name + ".png"))
    # 打印完成消息
    logger.info("Screenshot saved as %s.png" % name)

    return "success"


# 保存截图
def save_screenshot(screenshot_name, x, y, x2, y2):
    if not os.path.exists(spath(screenshot_name)) and x > 0:
        # 如果图片不存在,保存截图
        width = x2 - x
        height = y2 - y
        # 截取屏幕上的一个区域
        screenshot = pyautogui.screenshot(region=(int(x), int(y), int(width), int(height)))

        screenshot.save(spath(screenshot_name))


def typewrite(content, interval=0.3):
    # 使用这个方法需要注意一下系统的中英文输入法
    pyautogui.typewrite(content, interval)


def input_with_clipboard(content, inputEnter=False, sleep=1):
    try:
        # 将中文复制到剪贴板
        pyperclip.copy(content)
        time.sleep(1)
        # 模拟按下Ctrl+V粘贴
        pyautogui.hotkey('Ctrl', 'V')
        time.sleep(sleep)
        # 回车
        if inputEnter:
            pyautogui.hotkey('enter')
            time.sleep(1)
    except:
        return False
    return True


def input_words_with_clipboard(content_list):
    for content in content_list:
        if not input_with_clipboard(content, content.startswith(('@', '#'))):
            return False
    return True


def deal_content_to_list(content):
    try:
        return [part for part in re.split(r'([#@]\w+)|(\n)', content) if part is not None]
    except:
        return []

def press_hotkey(key='f5'):
    pyautogui.hotkey(key)
    time.sleep(1)


# 生成按钮截图
def generate_button_screenshot(screenshot_name, x=0, y=0, x2=0, y2=0):
    global _debug_
    _debug_ = True
    ## 生成按钮截图步骤
    # 0.删除旧的截图按钮
    # 1.打开对应的界面
    # 2.打开debug并执行一次方法，会产生界面截图
    # 3.根据截图找到要点击按钮的坐标
    # 4.填写要截图按钮的坐标
    # 5.再执行一次就会保存需要的按钮截图
    # 6.在执行一次,检查截图是否正确可用
    if check(screenshot_name):
        click(screenshot_name)

        logger.info("success")
        click("_next_page")
    else:
        save_screenshot(screenshot_name, x, y, x2, y2)


def scrollDown(y):
    try:
        pyautogui.scroll(y)
        time.sleep(2)
    except:
        return False
    return True



def check_with_region(screenshot_name, region):
    try:
        # pyautogui.locateOnScreen(spath(screenshot_name), confidence=0.85)
        x, y = pyautogui.center(pyautogui.locateOnScreen(spath(screenshot_name), region, confidence=0.85))
        logger.info("%s center: %s, %s" % (screenshot_name, x, y))
        return True
    except Exception as e:
        logger.error("%s check error: %s" % (screenshot_name, e))
        if _debug_:
            screenshot(screenshot_name + "_check_error")
    finally:
        pass
    return False


def click_with_region(screenshot_name, region, offset_x=0, offset_y=0, sleep=0.1):
    try:
        x, y = pyautogui.center(pyautogui.locateOnScreen(spath(screenshot_name), region, confidence=0.85))
        x = x + offset_x
        y = y + offset_y
        pyautogui.click(x, y)
        logger.info(" %s click: %s, %s" % (screenshot_name, x, y))
        time.sleep(sleep)
        return True
    except Exception as e:
        logger.error("%s click error: %s" % (screenshot_name, e))
        if _debug_:
            screenshot(screenshot_name + "_click_error")
    finally:
        pass
    return False


def press_hotkey_mult(key1, key2):
    try:
        pyautogui.hotkey(key1, key2)
        time.sleep(1)
    except:
        return False
    return True


def clickWithXY(x, y, offset_x=0, offset_y=0, sleep=0.1):
    try:
        x = x + offset_x
        y = y + offset_y
        pyautogui.click(x, y)
        logger.info(" click: %s, %s" % (x, y))
        time.sleep(sleep)
        return True
    except Exception as e:
        logger.error("click error: %s" % (e))
        if _debug_:
            screenshot("_click_error")
    finally:
        pass
    return False