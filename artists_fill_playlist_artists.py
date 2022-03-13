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
        artists
    WHERE
        calcartist != '-'""")

artist_names_couple = cur_artists.fetchall()

cur_artists.close()

print(len(artist_names_couple))
counter = 1

for artist in artist_names_couple:
    
    print(counter, artist[1])
    counter += 1
    
    cur_playlist_read.execute("""
        SELECT
            id
        FROM
            playlist
        WHERE clean_artist = ?
        """, (artist[0],))
     
    for row in cur_playlist_read:

            cur_playlist_write.execute("""
            UPDATE
                playlist
            SET
                calc_artist = ? where id = ?
            """, (artist[1], str(row[0])))

connection.commit()
cur_playlist_read.close()
cur_playlist_write.close()
