#clean values of existing db

##  CREATE TABLE "playlist" (
##	0 "id"	INTEGER,
##	1 "raw_tracklist_no"	INTEGER,
##	2 "raw_tracklist_item_no"	INTEGER,
##	3 "raw_tracklist_dj"	TEXT,
##	4 "raw_artist"	TEXT,
##	5 "raw_title"	TEXT,
##	6 "clean_status"	INTEGER,
##	7 "clean_tracklist_dj"	TEXT,
##	8 "clean_artist"	TEXT,
##	9 "clean_title"	TEXT,
##	10 "day"	INTEGER,
##	11 "month"	INTEGER,
##	12 "year"	INTEGER,
##	13 "days_from"	INTEGER,
##	14 "clean_dj_status"	INTEGER,

import re
import logging
from unidecode import unidecode
import sqlite3

#logging
if __name__ == "__main__":
    logger = logging.getLogger("run")
else:
    logger = logging.getLogger(__name__)
    
logger.setLevel(logging.INFO)

fh = logging.FileHandler('weloveradio1.log', encoding = "utf-8")
fh.setLevel(logging.DEBUG) # file loging level

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) # console loging level

fh_formatter = logging.Formatter('%(name)s | %(asctime)s | %(levelname)s | %(message)s')
ch_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')

ch.setFormatter(ch_formatter)
fh.setFormatter(fh_formatter)

logger.addHandler(ch)
logger.addHandler(fh)

# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')

#landscape
landscape_file = open("landscape.switch", "r")
landscape_switch = landscape_file.read()
landscape_file.close()
if landscape_switch == "PROD":
    landscape_data = ["weloveradio1db_P.sqlite"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1db_T.sqlite"]
else:
    landscape_data = ["weloveradio1db_D.sqlite"]
    
del_char = ["[",
            "]",
            "'",
            " "]

def clean_titles(titles):
    for s in del_char:
        titles = titles.replace(s, "")
    return(titles) 

def letterjoin(artist):
    artist = artist.replace("-","")
    artist = artist.split()
    artist = "".join(artist)
    return(artist)

def first_word(artist):
    artist = artist.replace("-","")
    artist = artist.split()
    return(artist[0])

def second_word(artist):
    artist = artist.replace("-","")
    artist = artist.split()
    if len(artist) > 1:
        artist = artist[1]
    else:
        artist = "-"
    return(artist)

    
try:
    connection = sqlite3.connect('weloveradio1db_D.sqlite') 
    cursor = connection.cursor()
    sql_select_query = """SELECT * from artists where id = ?"""
    sql_join_query = """UPDATE artists SET jnartist = ? where id = ?"""
    sql_first_word_query = """UPDATE artists SET first_word = ? where id = ?"""
    sql_second_word_query = """UPDATE artists SET second_word = ? where id = ?"""
    sql_clean_titles_query = """UPDATE artists SET titles = ? where id = ?"""
    sql_fill_calcartist_query = """UPDATE artists SET calcartist = "-" where id = ?"""    
   
    count = 0
    for row_id in range(1, 74395): #74395
        cursor.execute(sql_select_query, (row_id,))
        record = cursor.fetchone()
        
        cursor.execute(sql_join_query, (letterjoin(record[1]), row_id))
        cursor.execute(sql_first_word_query, (first_word(record[1]), row_id))
        cursor.execute(sql_second_word_query, (second_word(record[1]), row_id))
        cursor.execute(sql_clean_titles_query, (clean_titles(record[2]), row_id))
        cursor.execute(sql_fill_calcartist_query, (row_id,))
        
        count = count + 1
        
        if count == 1000:
            print(row_id)
            count = 0
    
    print ("/commit")
    connection.commit()
    cursor.close()

except sqlite3.Error as error:
    print("Failed: on row", error)
finally:
    if connection:
        connection.close()
        print("/db closed")
