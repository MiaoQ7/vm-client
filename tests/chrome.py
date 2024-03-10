import os
import time
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service


command = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"--user-data-dir=D:\browser_user_dir\browser_user_dir\chrome",
    f"--remote-debugging-port=16800",
    # 可以根据需要添加更多启动参数
    "--no-first-run",  # 可以帮助避免某些初次运行提示
    "--no-default-browser-check",  # 避免默认浏览器检查
    "--disable-features=Translate", # 禁用翻译
    "--disable-notifications" , #禁用通知
    'https://douyin.com'
]

subprocess.Popen(command, shell=True, stdout=None, stderr=None)
time.sleep(3)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:16800")
# service = Service(r"C:\Users\nyy\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(options=chrome_options)

# driver.get('https://channels.weixin.qq.com/platform/post/create')
time.sleep(3)
# while (True):
#     try:
#         element = driver.find_element(By.XPATH, '//input[@type="file"]')
#         if element:
#             print(element)
#             element.send_keys(r'Z:\resBak\video\upload_e98267ad213a2bb0ed82a656b7461b1a.mp4')
#             break
#     except:
#         pass

time.sleep(1000)

# def selectYear(driver, year):
#     years = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[2]/table/tbody/tr/td/a')
#     for y in years:
#         if y.text == year:
#             y.click()

# def selectMonth(driver, month):
#     months = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[2]/table/tbody/tr/td/a')
#     for m in months:
#         if m.text == month:
#             m.click()

# def selectDay(driver, day):
#     days = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[2]/table/tbody/tr/td/a')
#     for d in days:
#         if d.text == day:
#             d.click()

# def inputTime(driver, time):
#     # /html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[3]/dl/dt/span/div/span/input
#     ele = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dd/div/div[3]/dl/dt/span/div/span/input')
#     ele.send_keys(Keys.CONTROL,'a')
#     ele.send_keys(time)

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:16800")
# chrome = webdriver.Chrome(options=chrome_options)
# chrome.get('https://channels.weixin.qq.com/platform/post/create')
# time.sleep(30)
# # /html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dt/span[1]/div/span/input
# # //*[@id="container-wrap"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dt/span[1]/div/span/input
# # #container-wrap > div.container-center > div > div > div.main-body-wrap.post-create > div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form > div.post-time-wrap > div:nth-child(2) > div.form-item-body > dl > dt > span.weui-desktop-picker__value > div > span > input
# # weui-desktop-form__input
# while (True):
#     # /html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[1]/div[2]/div/label[2]/span
#     # /html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div/div[2]/div/label[2]/span
#     element = chrome.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div/div[2]/div/label[2]/span')
#     if element:
#         element.click()
#         input = chrome.find_element(By.XPATH,'//*[@id="container-wrap"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[7]/div[2]/div[2]/dl/dt/span[1]/div/span/input')
#         if input:
#             input.click()
#             selectYear(chrome, '2024')
#             selectMonth(chrome, '4')
#             selectDay(chrome, '1')
#             inputTime(chrome, '10:00')
#             break

time.sleep(1000)
