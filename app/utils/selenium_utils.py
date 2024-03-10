import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver import ActionChains
from loguru import logger


def find_element(driver=None, by_type=By.XPATH, param=None, traceID = ''):
    if not driver or not param:
        return None
    try:
        element = driver.find_element(by_type, param)
        if element:
            return element
        else:
            return None
    except Exception as e:
        logger.error("{} 获取元素失败 {} {}", traceID, param, e)
        return None
