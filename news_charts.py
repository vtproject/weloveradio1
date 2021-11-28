import sqlite3
import logging
import operator
import math

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

def last_week_tracks(from_day, to_day):
    
    from_day = to_day - 7
    to_day = to_day
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_artist, clean_title, COUNT(clean_title)
    FROM
        playlist
    WHERE days_from BETWEEN ? AND ? 
    GROUP BY
        clean_artist, clean_title
    HAVING
        COUNT(clean_title) > 1
    ORDER BY
        COUNT(clean_title) DESC,
        clean_artist ASC
    """, (str(from_day), str(to_day)))
    
    return(cursor.fetchall())
    cursor.close()
    
# def last_week_artists(from_day, to_day):
    
    # from_day = to_day - 7
    # to_day = to_day
    
    # cursor = connection.cursor()
    # cursor.execute("""
    # SELECT
        # clean_artist, COUNT(clean_artist)
    # FROM
        # playlist
    # WHERE days_from BETWEEN ? AND ? 
    # GROUP BY
        # clean_artist
    # HAVING
        # COUNT(clean_artist) > 1
    # ORDER BY
        # COUNT(clean_artist) DESC,
        # clean_artist ASC
    # """, (str(from_day), str(to_day)))
    
    # return(cursor.fetchall())
    # cursor.close()


def track_all_time(artist, title, actual_day):

    to_day = actual_day
    from_day = 0
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        COUNT(clean_title)
    FROM
        playlist
    WHERE clean_status = 1 AND clean_artist = ? AND clean_title = ? AND days_from BETWEEN ? AND ?     
    """, (artist, title, str(from_day),str(to_day)))
    
    record = cursor.fetchall()
    cursor.close()
    return(record[0][0])
      
# def artist_all_time(artist, actual_day):

    # to_day = actual_day
    # from_day = 0
    
    # cursor = connection.cursor()
    # cursor.execute("""
    # SELECT
        # COUNT(clean_artist)
    # FROM
        # playlist
    # WHERE clean_artist = ? AND days_from BETWEEN ? AND ?     
    # """, (artist, str(from_day),str(to_day)))
    
    # record = cursor.fetchall()
    # cursor.close()
 
    # return(record[0][0])

def main(from_day, to_day):       
    chart_tracks = last_week_tracks(from_day, to_day)

    tracks_out = []
    
    for track in chart_tracks:
        print("█", end = "", flush=True) #monitor
        if track[2] == track_all_time(track[0], track[1], to_day): 
            tracks_out.append([track[0], track[1],track[2]])
    
    return(tracks_out)
