import requests

session = requests.Session()

socks5 = f'socks5h://@161.117.180.69:23798'
proxies = {
  "http": socks5,
  "https": socks5
}
rsp = session.get('https://cgi1.apnic.net/cgi-bin/my-ip.php', proxies=proxies)
# rsp = session.get('https://ifconfig.io', proxies=proxies)
print(rsp.text)
