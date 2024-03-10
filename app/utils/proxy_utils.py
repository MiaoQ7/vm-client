from app.state.loop import bb,tt,fs
from loguru import logger
import winreg
import subprocess, time

localIP = '127.0.0.1'
localPort = 10500

def set_proxy(proxy_server):
    # 修改IE代理设置
    set_ie_proxy(proxy_server)

def set_ie_proxy(proxy_server):
    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as key:
        with winreg.OpenKey(key, r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_WRITE) as subkey:
            winreg.SetValueEx(subkey, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(subkey, 'ProxyServer', 0, winreg.REG_SZ, proxy_server)

def close_ie_proxy():
  with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as key:
    with winreg.OpenKey(key, r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_WRITE) as subkey:
        winreg.SetValueEx(subkey, 'ProxyEnable', 0, winreg.REG_DWORD, 0)

def _modify_local_proxy():
  set_proxy(f'{localIP}:{localPort}')


def change_proxy(type, ip, port, username, password):
  _modify_local_proxy()
  if type == 'socks5':
    if username:
      logger.info(f'pproxy -l http://{localIP}:{localPort} -r socks5://{ip}:{port}#{username}:{password}')
      subprocess.Popen(f'pproxy -l http://{localIP}:{localPort} -r socks5://{ip}:{port}#{username}:{password}', shell=True, stdout=None, stderr=None)
    else:
      subprocess.Popen(f'pproxy -l http://{localIP}:{localPort} -r socks5://{ip}:{port}', shell=True, stdout=None, stderr=None)

def close_proxy(handler):
  close_ie_proxy()
  subprocess.Popen('taskkill /F /IM pproxy.exe', shell=True, stdout=None, stderr=None).wait()

def use_tun2socks_proxy(type, ip, port, username, password):
  close_ie_proxy()
  if type == 'socks5':
    tun2socks_cmd = [bb.config.tun2socks_path + '\\tun2socks.exe', '-device', 'wintun', '-proxy', f'socks5://{username}:{password}@{ip}:{port}', '-interface', '以太网']
    # 启动 tun2socks 命令并保持在后台运行
    subprocess.Popen(tun2socks_cmd, cwd=bb.config.tun2socks_path)

    # 确保 tun2socks 已经启动
    time.sleep(5)  # 等待5秒以确保tun2socks启动

    # 执行 netsh 命令配置网络
    netsh_commands = [
        'netsh interface ipv4 set address name="wintun" source=static addr=192.168.123.1 mask=255.255.255.0',
        'netsh interface ipv4 set dnsservers name="wintun" static address=8.8.8.8 register=none validate=no',
        'netsh interface ipv4 add route 0.0.0.0/0 "wintun" 192.168.123.1 metric=1'
    ]

    for cmd in netsh_commands:
        subprocess.run(cmd, shell=True)

def close_tun2socks():
  # subprocess.Popen('taskkill /F /IM pproxy.exe', shell=True, stdout=None, stderr=None).wait()
  subprocess.Popen('taskkill /F /IM tun2socks.exe', shell=True, stdout=None, stderr=None).wait()


def pproxy_start(type, ip, port, username, password, no):
  if type == 'socks5':
    if username:
      logger.info(f'pproxy -l http://{localIP}:{localPort + no} -r socks5://{ip}:{port}#{username}:{password}')
      subprocess.Popen(f'pproxy -l http://{localIP}:{localPort + no} -r socks5://{ip}:{port}#{username}:{password}', shell=True, stdout=None, stderr=None)
    else:
      subprocess.Popen(f'pproxy -l http://{localIP}:{localPort + no} -r socks5://{ip}:{port}', shell=True, stdout=None, stderr=None)

def pproxy_stop(no):
  process = subprocess.Popen(f'netstat -ano | findstr 127.0.0.1:{localPort + no}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  tmp = list(filter(lambda a: a,stdout.decode().replace('\r\n', '').split(' ')))
  if (len(tmp) > 4):
    subprocess.Popen(f'taskkill /pid {tmp[4]} -t -f', shell=True, stdout=None, stderr=None).wait()
