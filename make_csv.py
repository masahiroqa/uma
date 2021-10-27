import datetime
import pytz
now_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

import time
import re
import os
from os import path
OWN_FILE_NAME = path.splitext(path.basename(__file__))[0]
OWN_URL_DIR = "race_url"
RACR_HTML_DIR = "race_html"
CSV_DIR = "csv"

import logging
logger = logging.getLogger(__name__)

race_data_columns=[
    'race_id', # サイトにおけるユニークなレースID
    'race_round', #何レース目か
    'race_title', #レースのタイトル
    'race_course', #ダ左1400m みたいな走るコース
    'weather', #天気
    'ground_status', #地面の状態 e.g. [ダ: 良]
    'time', #開始時間
    'date', #開催日時
    'where_racecourse', #レースの開催場所 e.g. 東京、大阪とか
    'total_hourse_number', #出馬した馬の数
    'frame_number_first', #1着の枠番
    'hourse_number_first', #1着の馬番
    'frame_number_second', #2着の枠番
    'hourse_number_second', #2着の馬番
    'frame_number_third', #3着の枠番
    'hourse_number_third', #3着の馬番
    'tansyo', # 単勝 100円かけた場合の返還金額
    'hukusyo_first', # 複勝 1着
    'hukusyo_second', # 複勝 2着
    'hukusyo_third', #複勝 ３着
    'wakuren', # 枠連
    'wide_1_2', # ワイド
    'wide_1_3', # ワイド
    'wide_2_3', # ワイド
    'umatan', #馬単
    'renhuku3', # 三連複
    'rentan3' # 三連単
]

horse_data_columns=[
    'race_id', # サイトにおけるユニークなレースID
    'rank', #レースにおける着順
    'frame_number', #レースにおける枠番
    'horse_number', #馬番
    'horse_id', # サイトにおける馬のid /horse/horse_id　で検索すると拾える
    'sex_and_age', #性別と年齢
    'burden_weight', #斥量
    'rider_id', #騎手ID
    'goal_time', #ゴールタイム
    'goal_time_dif', #着差
    'time_value', # タイム指数
    'half_way_rank', #通過
    'last_time', #上り
    'odds', #オッズ
    'popular', #人気
    'horse_weight', #体重
    'tame_time', # 調教タイム
    'tamer_id', #調教師 id
    'owner_id', #　オーナーID
    'horse_name', #馬の名前
    'rider_name', #騎手の名前
    'tamer_name', #調教師の名前
    'owner_name' # オーナーの名前
]

def make_csv_from_html():
    for year in range(2008, now_datetime.year+1):
        make_csv_from_html_by_year(year)

def make_csv_from_html_by_year(year):
    save_race_csv = CSV_DIR+"/race-"+str(year)+".csv"
    horse_race_csv = CSV_DIR+"/horse-"+str(year)+".csv"
    if not ((os.path.isfile(save_race_csv)) and (os.path.isfile(horse_race_csv))):
        race_df = pd.DataFrame(columns=race_data_columns)
        horse_df = pd.DataFrame(columns=horse_data_columns)
        logger.info("saving csv (" + str(year) +")")
        total = 0
        for month in range (1,13):
            html_dir = RACR_HTML_DIR+"/"+str(year)+"/"+str(month)
            if os.path.isdir(html_dir):
                file_list = os.listdir(html_dir)
                total += len(file_list)
                logger.info(" appending " + str(len(file_list)) + " datas to csv (" + str(year)  +" "+ str(month)+ ")")
                for file_name in file_list:
                    with open(html_dir+"/"+file_name, "r") as f:
                        html = f.read()
                        list = file_name.split(".")
                        race_id = list[-2]
                        race_list, horse_list_list = get_rade_and_horse_data_by_html(race_id, html)
                        for horse_list in horse_list_list:
                            horse_se = pd.Series(horse_list, index=horse_df.columns)
                            horse_df = horse_df.append(horse_se, ignore_index=True)
                        race_se = pd.Series(race_list, index=race_df.columns)
                        race_df = race_df.append(race_se, ignore_index=True)
        race_df.to_csv(save_race_csv, header=True, index=False)
        horse_df.to_csv(horse_race_csv, header=True, index=False)
        logger.info(' (rows, columns) of race_df:\t'+ str(race_df.shape))
        logger.info(' (rows, columns) of horse_df:\t'+ str(horse_df.shape))
        logger.info("saved " + str(total) + " htmls to csv (" + str(year) +")")
    else:
        logger.info("already have csv (" + str(year) +")")

def get_rade_and_horse_data_by_html(race_id, html):
    race_list = [race_id]
    horse_list_list = []
    soup = BeautifulSoup(html, 'html.parser')

    data_intro = soup.find("div", class_="data_intro")
    race_list.append(data_intro.find("dt").get_text().strip("\n")) #race round
    race_list.append(data_intro.find("h1").get_text().strip("\n")) #race title
    race_details1 = data_intro.find("p").get_text().strip("\n").split("\xa0/\xa0")
    race_list.append(race_details1[0]) #race course
    race_list.append(race_details1[1]) #weather
    race_list.append(race_details1[2]) #ground status
    race_list.append(race_details1[3]) #time
    race_details2 = data_intro.find("p", class_="smalltxt").get_text().strip("\n").split(" ")
    race_list.append(race_details2[0]) #date
    race_list.append(race_details2[1]) #where racecourse

    result_rows = soup.find("table", class_="race_table_01 nk_tb_common").findAll('tr') #レース結果
    race_list.append(len(result_rows)-1) #total horse number
    #上位3着分を取得
    for i in range(1, 4):
        row = result_rows[i].findAll('td')
        race_list.append(row[1].get_text()) # frame number first or second or third
        race_list.append(row[2].get_text()) # horse number first or second or third

    # 払い戻し(単勝, 複勝, 三連複, 三連単)
    pay_back_tables =  soup.findAll("table", class_="pay_table_01")

    pay_back1 = pay_back_tables[0].findAll('tr')
    race_list.append(pay_back1[0].find("td", class_="txt_r").get_text()) #tansyo
    hukuren = pay_back1[1].find("td", class_="txt_r")
    tmp =  []
    for string in hukuren.strings:
        tmp.append(string)
    for i in range(3):
        try:
            race_list.append(tmp[i]) #hukuren first or second or third
        except IndexError:
            race_list.append("0")
    
    try:
        race_list.append(pay_back1[2].find("td", class_="txt_r").get_text()) #wakuren
    except IndexError:
        race_list.append("0")

    pay_back2 = pay_back_tables[1].findAll('tr')

    wide = pay_back2[0].find("td", class_="txt_r")
    tmp = []
    for string in wide.strings:
        tmp.append(string)
    for i in range(3):
        try:
            race_list.append(tmp[i]) # hukuren first or second or third
        except IndexError:
            race_list.append("0")
    
    race_list.append(pay_back2[1].find("td", class_="txt_r").get_text()) #umatan
    race_list.append(pay_back2[2].find("td", class_="txt_r").get_text()) #renhuku3
    try:
        race_list.append(pay_back2[3].find("td", class_="txt_r").get_text()) # rentan3
    except IndexError:
        race_list.append("0")

    # horse data
    for rank in range(1, len(result_rows)):
        horse_list = [race_id]
        result_row = result_rows[rank].findAll("td")
        horse_list.append(result_row[0].get_text()) #rank
        horse_list.append(result_row[1].get_text()) #frame number
        horse_list.append(result_row[2].get_text()) #horse_number
        horse_list.append(result_row[3].find('a').get('href').split("/")[-2]) #horse_id
        horse_name = result_row[3].get_text() 
        horse_list.append(result_row[4].get_text()) # sex and age
        horse_list.append(result_row[5].get_text()) # burden weight
        horse_list.append(result_row[6].find('a').get('href').split("/")[-2]) #rider_id
        rider_name = result_row[3].get_text()
        horse_list.append(result_row[7].get_text())  # goal_time
        horse_list.append(result_row[8].get_text()) # goal_time_dif
        horse_list.append(result_row[9].get_text())  # time_value(premium)
        horse_list.append(result_row[10].get_text()) # half_way_rank
        horse_list.append(result_row[11].get_text()) # last_time(上り)
        horse_list.append(result_row[12].get_text()) # odds
        horse_list.append(result_row[13].get_text()) # popular
        horse_list.append(result_row[14].get_text()) # horse_weight
        horse_list.append(result_row[15].get_text()) # tame_time(premium)
        horse_list.append(result_row[18].find('a').get('href').split("/")[-2]) # tamer_id
        tamer_name = result_row[18].get_text()
        horse_list.append(result_row[19].find('a').get('href').split("/")[-2]) # owner_id
        owner_name = result_row[19].get_text()
        horse_list.append(horse_name)
        horse_list.append(rider_name)
        horse_list.append(tamer_name)
        horse_list.append(owner_name)


        horse_list_list.append(horse_list)

    return race_list, horse_list_list

if __name__ == '__main__':
    formatter = "%(asctime)s [%(levelname)s]\t%(message)s" # フォーマットを定義
    #formatter_func = "%(asctime)s\t[%(levelname)8s]\t%(message)s from %(func)" # フォーマットを定義
    logging.basicConfig(filename='logfile/'+OWN_FILE_NAME+'.logger.log', level=logging.INFO, format=formatter)

    logger.info("start making csv!")
    make_csv_from_html()
