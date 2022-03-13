import sqlite3
import logging
import operator
import math

import artists_match

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

# max from day = 3436    

# first run:
from_day = 0
to_day = 3436 -10

# from_day = 3436 - 9
# to_day = 3436 - 9 = 3427

cursor = connection.cursor()
cursor.execute("""
    SELECT
        clean_artist, COUNT(clean_artist)
    FROM   (SELECT
        clean_artist
    FROM
        playlist
    WHERE clean_status = 1 AND days_from BETWEEN ? AND ?
    GROUP BY
        clean_artist, raw_tracklist_no)
    GROUP BY 
        clean_artist
    HAVING
        COUNT(clean_artist) > 300 
    ORDER BY
        COUNT(clean_artist) DESC,
        clean_artist ASC
        
""", (str(from_day), str(to_day)))
  
chart_unsorted = cursor.fetchall()

print(len(chart_unsorted))
input()

cursor.execute("""
    SELECT
        clartist, id
    FROM
        artists""")

artist_ids = dict(cursor.fetchall())
cursor.close()

ids = []
for artist in chart_unsorted:
    ids.append(artist_ids[artist[0]])

print(len(ids))

artists_match.main(ids)