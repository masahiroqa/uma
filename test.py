from get_url import OWN_FILE_NAME, get_race_url

import sys
import traceback
import requests
import os
from os import path

OWN_FILE_NAME = path.splitext(path.basename(__file__))[0]

import logging

logger = logging.getLogger(__name__)

def update():
    get_race_url()

if __name__ == '__main__':
    try:
        formatter_func = "%(asctime)s - %(module)s.%(funcName)s [%(levelname)s]\t%(message)s" # フォーマットを定義
        logging.basicConfig(filename='logfile/'+OWN_FILE_NAME+'.logger.log', level=logging.INFO, format=formatter_func)
        logger.info("start updating!")
        update()
    except Exception as e:
        t, v, tb = sys.exc_info()
        for str in traceback.format_exception(t,v,tb):
            str = "\n"+str
            logger.error(str)
