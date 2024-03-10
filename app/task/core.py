import uuid, time

from app.state.loop import bb,tt,fs
from app.libs import ihttp
from loguru import logger
from app.utils import ip_utils, browser_utils, proxy_utils, win_utils

def _get_url(appType):
  # appTypes = ["dy", "tk", "sph", "xhs", "yt", "tw", "google"]
  if appType == 'dy':
    return 'https://www.douyin.com/'
  if appType == 'tk':
    return 'https://www.tiktok.com/'
  if appType == 'sph':
    return 'https://channels.weixin.qq.com/'
  if appType == 'xhs':
    return 'https://www.xiaohongshu.com/'
  if appType == 'yt':
    return 'https://www.youtube.com/'
  if appType == 'tw':
    return 'https://twitter.com/'
  if appType == 'google':
    return 'https://www.google.com/'
  return ''

def start():
  return "success"

def get_task():
  try:
    # 请求注册开关
    for browser in bb.config.browserTypes:
      for appType in bb.config.appTypes:
        # resp = ihttp.post(
        #   url=f"{bb.config.gatewayServerURL + bb.config.getTaskURL}", json={"machineId":tt.get_machine_id() + "," + browser + "," + appType + "," + ip_utils.get_mac() + "," + ip_utils.get_local_ip()}
        # )
        # if resp.ok:
        # data = resp.json()
        # login
        # data = {
        #   'code': 0,
        #   'api': 'openBrowser',
        #   'data': {}
        # }

        # 发视频
        data = {
          'code': 0,
          'api': 'send_post',
          'data': {
            'video': '1.mp4', # 视频
            'title': '', # 标题
            'desc': '', # 描述
            'location': '', # 定位
            'pub_time': '', # 定时发送时间
          }
        }
        logger.info(data)
        if data["code"] == 0:
          bb.browser = browser
          bb.appType = appType
          bb.task = data
          bb[bb.task['api']] = 0
          api = bb.task['api']
          if api == 'openBrowser':
            return "openBrowser"
          if api == 'logout':
            return "logout"
          return appType + '_' + bb.task['api']
  except:
    pass

  return "failed"

def set_proxy():
  try:
    return "success"
  except:
    pass

  return "failed"

def openBrowser():
  if (bb.openBrowser and bb.openBrowser >= 5):
    bb.openBrowser = 0
    return "timeout"
  try:
    # browser_utils.open_firefox('http://google.com')
    tz = bb.task['data'].get('tz')
    if (tz):
      win_utils.set_system_timezone(tz)
    lang = bb.task['data'].get('lang')
    if (lang):
      win_utils.set_system_language(lang)
    url = _get_url(bb.appType)
    proxy_utils.close_tun2socks()
    # if bb.task['data'].get('ip'):
    #   proxy_utils.use_tun2socks_proxy('socks5', bb.task['data']['ip'], bb.task['data']['port'], bb.task['data']['username'], bb.task['data']['password'])
    # ["chrome", "edge", "firefox", "opera", "qq"]
    if bb.browser.startswith('chrome'):
      if not browser_utils.open_chrome_user_dir(url, bb.browser + '_' + bb.appType):
        raise Exception('open browser error')
    if bb.browser == 'firefox':
      browser_utils.open_firefox(url)
    if bb.browser == 'opera':
      browser_utils.open_opera(url)
    if bb.browser == 'edge':
      browser_utils.open_edge(url)
    if bb.browser == 'qq':
      browser_utils.open_qqbrowser(url)
    return "success"
  except Exception as e:
    logger.error(e)
  if bb.openBrowser:
    bb.openBrowser += 1
  else:
    bb.openBrowser = 1
  return "failed"

def logout():
  if bb.browser.startswith('chrome'):
    browser_utils.logout_chrome(bb.browser + '_' + bb.appType)
  return 'success'

def testBrowser():
  # browser_utils.logout_chrome('chrome_1')
  # browser_utils.open_chrome_user_dir('http://google.com', 'chrome_1')
  # time.sleep(3)
  # browser_utils.open_chrome_user_dir('http://google.com', 'chrome_2')
  # time.sleep(3)
  # browser_utils.open_chrome_user_dir('http://google.com', 'chrome_3')
  # time.sleep(3)
  # browser_utils.open_chrome_user_dir('http://google.com', 'chrome_4')
  # time.sleep(3)
  # browser_utils.open_firefox('http://google.com')
  # time.sleep(3)
  # browser_utils.open_edge('http://google.com')
  # time.sleep(3)
  # browser_utils.open_opera('http://google.com')
  # time.sleep(3)
  # browser_utils.open_qqbrowser('http://google.com')
  return "success"

def feedtask():
  if (bb.feedtask and bb.feedtask >= 5):
    bb.feedtask=0
    return "timeout"
  resp = ihttp.post(
    url=f"{bb.config.gatewayServerURL + bb.config.feedbackTask}", json={
      "machineId":tt.get_machine_id() + "," + bb.browser + "," + bb.appType + "," + ip_utils.get_mac() + "," + ip_utils.get_local_ip(),
      "taskId": bb.task['taskId'],
      "result": "success"
    }
  )
  if resp.ok:
    data = resp.json()
    if data["code"] == 0:
      return 'success'
    else:
      if bb.feedtask:
        bb.feedtask += 1
      else:
        bb.feedtask = 1
      return 'failed'

def feedtask_error():
  if (bb.feedtask_error and bb.feedtask_error >= 5):
    bb.feedtask_error = 0
    return "timeout"
  resp = ihttp.post(
    url=f"{bb.config.gatewayServerURL + bb.config.feedbackTask}", json={
      "machineId":tt.get_machine_id() + "," + bb.browser + "," + bb.appType + "," + ip_utils.get_mac() + "," + ip_utils.get_local_ip(),
      "taskId": bb.task['taskId'],
      "result": "timeout"
    }
  )
  if resp.ok:
    data = resp.json()
    if data["code"] == 0:
      return 'success'
    else:
      if bb.feedtask_error:
        bb.feedtask_error += 1
      else:
        bb.feedtask_error = 1
      return 'failed'