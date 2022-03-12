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
cur_artists = connection.cursor()
cur_playlist_read = connection.cursor()
cur_playlist_write = connection.cursor()

cur_artists.execute("""
    SELECT
        clartist, calcartist
    FROM
        artists""")

artist_names_dict = dict(cur_artists.fetchall())

cur_artists.close()

# max from day = 3436    

# first run:
# from_day = 3436 - 7 - 10 = 3419
# to_day = 3436 -10

# from_day = 3436 - 9
# to_day = 3436 - 9 = 3427

day = 3419

for day in range(3421, 3428):
    print(day)
    cur_playlist_read.execute("""
        SELECT
            id, clean_artist, calc_artist
        FROM
            playlist
        WHERE clean_status = 1 AND days_from = ?
        """, (str(day),))
     
    for row in cur_playlist_read:
        if artist_names_dict[row[1]] == "-":
            print("X")
        else:
            cur_playlist_write.execute("""
            UPDATE
                playlist
            SET
                calc_artist = ? where id = ?
            """, (artist_names_dict[row[1]], str(row[0])))

connection.commit()
cur_playlist_read.close()
cur_playlist_write.close()
