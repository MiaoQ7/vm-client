from app.state.loop import bb,tt,fs
from app.libs import ihttp
from loguru import logger
import subprocess
import os,time,psutil
import win32gui,win32process,pythoncom,win32con
from win32com import client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
from app.utils import proxy_utils
# from selenium.webdriver.chrome.service import Service

# service = Service(bb.config.chromeCanaryDriverPath)
init_port = 16800
_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
browser_user_dir = os.path.join(_parent_dir, 'browser_user_dir')

if not os.path.exists(browser_user_dir):
  os.mkdir(browser_user_dir)

def is_port_open(ip, port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect((ip, port))
    s.shutdown(2)
    return True
  except:
    return False

def _top(name):
  time.sleep(3)
  mID2Handle={}
  mID2Handle[name]=''
  def get_all_hwnd(hwnd,mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
      nID=win32process.GetWindowThreadProcessId(hwnd)
      del nID[0]
      for abc in nID:
        try:
          pro=psutil.Process(abc).name()
        except psutil.NoSuchProcess:
          pass
        else:
          #print(abc,win32gui.GetWindowText(hwnd))
          if pro.lower() == name.lower():
            print("top进程ID：",abc,"窗口句柄: ",hwnd,"标题: ",win32gui.GetWindowText(hwnd))
            mID2Handle[name]=hwnd
  win32gui.EnumWindows(get_all_hwnd, 0)
  _hwnd = mID2Handle[name]
  if _hwnd:
    try:
      # 窗口需要最大化且在后台，不能最小化
      win32gui.ShowWindow(_hwnd, win32con.SW_SHOWMAXIMIZED)
      pythoncom.CoInitialize()
      shell = client.Dispatch("WScript.Shell")
      shell.Sendkeys('%')
      shell.Sendkeys('%')
      win32gui.SetForegroundWindow(_hwnd)
    except:
      pass

def _close(name):
  mID2Handle={}
  mID2Handle[name] = 0
  def get_all_hwnd(hwnd,mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
      nID=win32process.GetWindowThreadProcessId(hwnd)
      del nID[0]
      for abc in nID:
        try:
          pro=psutil.Process(abc).name()
        except psutil.NoSuchProcess:
          pass
        else:
          #print(abc,win32gui.GetWindowText(hwnd))
          if pro.lower() == name.lower():
            print("close进程ID：",abc,"窗口句柄: ",hwnd,"标题: ",win32gui.GetWindowText(hwnd))
            mID2Handle[name]=hwnd
  win32gui.EnumWindows(get_all_hwnd, 0)
  _hwnd = mID2Handle[name]
  if _hwnd:
    try:
      win32gui.PostMessage(_hwnd, win32con.WM_CLOSE, 0, 0)
    except:
      pass

def _kill_all_browser():
  # _close('chrome.exe')
  # _close('firefox.exe')
  # _close('opera.exe')
  # _close('msedge.exe')
  # _close('QQBrowser.exe')
  # time.sleep(1)
  # subprocess.Popen("taskkill /F /IM chrome.exe", shell=True, stdout=None, stderr=None).wait()
  # subprocess.Popen("taskkill /F /IM firefox.exe", shell=True, stdout=None, stderr=None).wait()
  # subprocess.Popen("taskkill /F /IM opera.exe", shell=True, stdout=None, stderr=None).wait()
  # subprocess.Popen("taskkill /F /IM msedge.exe", shell=True, stdout=None, stderr=None).wait()
  # subprocess.Popen("taskkill /F /IM qqbrowser.exe", shell=True, stdout=None, stderr=None).wait()
  for browser in bb.config.browserTypes:
    for appType in bb.config.appTypes:
      if (bb.get(f'{browser}_{appType}')):
        try:
          bb.get(f'{browser}_{appType}').close()
        except:
          pass
        bb['{browser}_{appType}'] = None
      subprocess.Popen(f"taskkill /F /IM {browser}_{appType}.exe", shell=True, stdout=None, stderr=None).wait()

def _copyfile(source, target):
  with open(source, "rb") as source_file:
      with open(target, "wb") as target_file:
          target_file.write(source_file.read())

def close_browser(name):
  _close(name)
  subprocess.Popen("taskkill /F /IM " + name, shell=True, stdout=None, stderr=None).wait()

def open_chrome_user_dir(url, name):
  _kill_all_browser()
  no = int(name.split('_')[1])
  use_proxy = False
  proxy_utils.pproxy_stop(no)
  if bb.task['data'].get('ip'):
    use_proxy = True
    proxy_utils.pproxy_start('socks5', bb.task['data']['ip'], bb.task['data']['port'], bb.task['data']['username'], bb.task['data']['password'], no)
  exec_name = name + '.exe'
  if (bb.get(name)):
    try:
      bb.get(name).close()
    except:
      pass
    bb[name] = None
  close_browser(exec_name)
  source = os.path.join(bb.config.chromeCanaryPath, 'chrome.exe')
  target = os.path.join(bb.config.chromeCanaryPath, exec_name)
  if not os.path.exists(target):
    _copyfile(source, target)
  user_dir = os.path.join(browser_user_dir, name)
  if not os.path.exists(user_dir):
    os.mkdir(user_dir)
  remote_debugging_port = init_port + no

  if use_proxy:
    command = [
      target,
      f"--remote-debugging-port={remote_debugging_port}",
      f"--user-data-dir={user_dir}",
      # 可以根据需要添加更多启动参数
      "--no-first-run",  # 可以帮助避免某些初次运行提示
      "--no-default-browser-check",  # 避免默认浏览器检查
      "--disable-features=Translate", # 禁用翻译
      "--disable-notifications" , #禁用通知
      f"--proxy-server=http://{proxy_utils.localIP}:{proxy_utils.localPort + no}",
      url
    ]
  else:
    command = [
      target,
      f"--remote-debugging-port={remote_debugging_port}",
      f"--user-data-dir={user_dir}",
      # 可以根据需要添加更多启动参数
      "--no-first-run",  # 可以帮助避免某些初次运行提示
      "--no-default-browser-check",  # 避免默认浏览器检查
      "--disable-features=Translate", # 禁用翻译
      "--disable-notifications" , #禁用通知
      url
    ]
  subprocess.Popen(command, shell=True, stdout=None, stderr=None)
  time.sleep(2)
  _top(exec_name)

  if is_port_open('127.0.0.1', remote_debugging_port):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{remote_debugging_port}")

    driver = webdriver.Chrome(options=chrome_options)
    bb[name] = driver
    return True
  else:
    bb[name] = None
    return False

def remove_dir(path):
  if os.path.isdir(path):
    for file in os.listdir(path):
      file_path = os.path.join(path, file)
      if os.path.isdir(file_path):
        remove_dir(file_path)
      else:
        os.remove(file_path)
    os.rmdir(path)

def logout_chrome(name):
  no = int(name.split('_')[1])
  proxy_utils.pproxy_stop(no)
  exec_name = name + '.exe'
  if (bb.get(name)):
    try:
      bb.get(name).close()
    except:
      pass
    bb[name] = None
  close_browser(exec_name)
  time.sleep(3)
  user_dir = os.path.join(browser_user_dir, name)
  if os.path.exists(user_dir):
    remove_dir(user_dir)

def open_chrome(url):
  _kill_all_browser()
  os.chdir(bb.config.chromePath)
  subprocess.Popen(f'chrome.exe {url}', shell=True, stdout=None, stderr=None)
  time.sleep(2)
  _top('chrome.exe')

def open_firefox(url):
  _kill_all_browser()
  os.chdir(bb.config.firefoxPath)
  subprocess.Popen(f'firefox.exe -new-window {url}', shell=True, stdout=None, stderr=None).wait()
  _top('firefox.exe')

def open_opera(url):
  _kill_all_browser()
  os.chdir(bb.config.operaPath)
  subprocess.Popen(f'opera.exe {url}', shell=True, stdout=None, stderr=None).wait()
  _top('opera.exe')

def open_edge(url):
  _kill_all_browser()
  os.chdir(bb.config.edgePath)
  subprocess.Popen(f'msedge.exe {url}', shell=True, stdout=None, stderr=None)
  _top('msedge.exe')

def open_qqbrowser(url):
  _kill_all_browser()
  os.chdir(bb.config.qqbrowserPath)
  subprocess.Popen(f'QQBrowser.exe {url}', shell=True, stdout=None, stderr=None)
  _top('QQBrowser.exe')
