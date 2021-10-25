import time
import datetime
import pytz
now_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

import re
import os
from os import path
OWN_PATH_NAME = path.splitext(path.basename(__file__))
RACE_URL_DIR = "race_URL"

import logging
logger = logging.getLogger(__name__)

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver import chrome
from selenium.webdriver.chrome import options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = "https://db.netkeiba.com/?pid=race_search_detail"
WAIT_SECOND = 1

def get_race_url():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    for year in range(2000, now_datetime.year):
        for month in range(1, 13):
            race_url_file = RACE_URL_DIR + "/" + str(year) + "-" + str(month) + ".txt"
            if not os.path.isfile(race_url_file):
                logger.info("getting urls ("+str(year)+" "+str(month)+ ")")
                get_race_url_by_year_and_mon(driver, year, month)
    logger.info("getting urls ("+str(now_datetime.year)+" "+str(now_datetime.month)+ ")")

    driver.close
    driver.quit

def get_race_url_by_year_and_mon(driver, year, month):
    race_url_file = RACE_URL_DIR + "/" + str(year) + "-" + str(month) + ".txt"

    wait = WebDriverWait(driver, 10)