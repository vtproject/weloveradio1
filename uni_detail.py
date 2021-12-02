import sqlite3
import datetime
import urllib.parse
import re
import logging

def date_out(datum):
    date_out_f = str(datum)
    date_out_f = datetime.datetime.strptime(date_out_f, '%Y-%m-%d')
    date_out_f = date_out_f.strftime('%#d.%#m.%Y')
    return date_out_f


#logging
if __name__ == "__main__":
    logger = logging.getLogger("run")
else:
    logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

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
    landscape_data = ["weloveradio1db_P.sqlite", "html_P/"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1db_T.sqlite", "html_T/"]
else:
    landscape_data = ["weloveradio1db_D.sqlite", "html_D/"]

connection = sqlite3.connect(landscape_data[0])

def djs_month_back(artist, title, actual_day):

    to_day = actual_day
    from_day = actual_day - 30
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_tracklist_dj, day, month, year
    FROM
        playlist
    WHERE clean_artist = ? AND clean_title = ? AND days_from BETWEEN ? AND ? 
    ORDER BY
        year DESC,
        month DESC,
        day DESC;
    """, (artist, title, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record)

def tracks_month_back(artist, actual_day):

    to_day = actual_day
    from_day = actual_day - 30
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_title, clean_tracklist_dj,  day, month, year
    FROM
        playlist
    WHERE clean_artist = ? AND days_from BETWEEN ? AND ? 
    ORDER BY
        year DESC,
        month DESC,
        day DESC;
    """, (artist, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record)
    
def djs_week_back(artist, title, actual_day):

    to_day = actual_day
    from_day = actual_day - 6
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_tracklist_dj, day, month, year
    FROM
        playlist
    WHERE clean_artist = ? AND clean_title = ? AND days_from BETWEEN ? AND ? 
    ORDER BY
        year DESC,
        month DESC,
        day DESC;
    """, (artist, title, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record)

def djs_summ_beyond_month(artist, title, actual_day):

    to_day = actual_day - 30
    from_day = 0
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_tracklist_dj, COUNT(clean_tracklist_dj)
    FROM
        playlist
    WHERE clean_artist = ? AND clean_title = ? AND days_from BETWEEN ? AND ?
    GROUP BY
        clean_tracklist_dj    
    ORDER BY
        COUNT(clean_tracklist_dj) DESC;
    """, (artist, title, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record)
    
def tracks_summ_beyond_month(artist, actual_day):

    to_day = actual_day - 30
    from_day = 0
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_title, COUNT(clean_tracklist_dj)
    FROM
        playlist
    WHERE clean_artist = ? AND days_from BETWEEN ? AND ?
    GROUP BY
        clean_title   
    ORDER BY
        COUNT(clean_tracklist_dj) DESC;
    """, (artist, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record)
    
def dj_first_play(artist, title, actual_day):

    to_day = actual_day - 30
    from_day = 0
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_tracklist_dj, day, month, year
    FROM
        playlist
    WHERE clean_artist = ? AND clean_title = ? AND days_from BETWEEN ? AND ? 
    ORDER BY
        year DESC,
        month DESC,
        day DESC;
    """, (artist, title, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record[-1])

def track_first_play(artist, actual_day):

    to_day = actual_day - 30
    from_day = 0
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_title, clean_tracklist_dj, day, month, year
    FROM
        playlist
    WHERE clean_artist = ? AND days_from BETWEEN ? AND ? 
    ORDER BY
        year DESC,
        month DESC,
        day DESC;
    """, (artist, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    
    if not record:
        return("není")
    else:    
        return(record[-1])    
   
# update_date = datetime.date.today()  # Datum generování datetime.date(2021, 4, 3)  datetime.date.today() 
# execute_date = update_date - datetime.timedelta(1) # Datum generování html  
# actual_day = execute_date - datetime.date(2012, 9, 29)
# actual_day = actual_day.days

# artist_in = "ARLETA"
# title_in = "Statement"

# print(artist_in)
# print(title_in)
# print()
# print("djs_week_back", djs_week_back(artist_in, title_in, actual_day))
# print()
# print("djs_month_back", djs_month_back(artist_in, title_in, actual_day))
# print()
# print("djs_summ_beyond_month", djs_summ_beyond_month(artist_in, title_in, actual_day))
# print()
# print("dj_first_play", dj_first_play(artist_in, title_in, actual_day))
# print()
# print("tracks_month_back", tracks_month_back(artist_in, actual_day))
# print()
# print("tracks_summ_beyond_month", tracks_summ_beyond_month(artist_in, actual_day))
# print()
# print("track_first_play", track_first_play(artist_in, actual_day))
