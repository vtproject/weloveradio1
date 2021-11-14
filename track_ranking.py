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

def retrieve_chart_tracks(from_day, to_day, days_back):
    cursor = connection.cursor()
   
    cursor.execute("""
    SELECT
        clean_artist, clean_title, COUNT(clean_title)
    FROM
        playlist
    WHERE clean_status = 1 AND days_from BETWEEN """ + str(from_day) + """ AND """ + str(to_day) + """
    GROUP BY
        clean_artist, clean_title
    HAVING
        COUNT(clean_title) > 61    
    ORDER BY
        COUNT(clean_title) DESC,
        clean_artist ASC;
    """)
    return(cursor.fetchall())
    cursor.close()
    

def main(artist, title):
 
    try:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT
            clean_tracklist_dj, days_from
        FROM
            playlist
        WHERE clean_artist = ? AND clean_title = ?
        ORDER BY
            days_from DESC;
        """, (artist, title))
        
        track_record = cursor.fetchall()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("""
        SELECT
            days_from
        FROM
            playlist
        WHERE clean_artist = ? 
        """, (artist,))
        
        artist_record = cursor.fetchall()
        cursor.close()
        
        djindex = len(set([item[0] for item in track_record])) #počet djs, kteří skladbu hráli celkem
        track_play_index = len(track_record) #počet hraní skaladby celkem
        artist_play_index = len(artist_record) #počet hraní skupiny celkem
        
        timediff=[]
        for item in range(0,len(track_record)-1):
            timediff.append(track_record[item][1] - track_record[item+1][1])
        time_diff_index=(sum(timediff)/len(timediff)) #průměrný počet dní mezi hraním skladby   
        if time_diff_index == 0:
            time_diff_index = 2
        else:
            time_diff_index = 1/time_diff_index 
        return([djindex, track_play_index, time_diff_index, artist_play_index])
     
        
    except sqlite3.Error as error:
        logger.error("Failed:%s", error)


chart=retrieve_chart_tracks(1497, 3322, 0)

indexed_chart = []
cnt=1
 
for track in chart:
    raw_index = main(track[0], track[1])
    index = (str(track[2]).zfill(3) + "." + #počet přehrání skladby v období
             str(raw_index[0]).zfill(2) + "." + #počet djs celkem, kteří skladbu hráli
             str(raw_index[1]).zfill(3) + "." + #počet přehrání skladby celkem
             str(math.trunc(raw_index[2]*1000)).zfill(4) + "." + #převrácená hodnota průměrné četnosti hraní skladby ve dnech
             str(raw_index[3]).zfill(4)) #počet přehrání skupiny celkem
    indexed_chart.append([index, track[0], track[1]])
    i = (cnt/len(chart))*100
    print('Processing %i%%\r'%i, end="") #zobrazení procenta
    cnt+=1

indexed_chart.sort(key=operator.itemgetter(0), reverse = True) #seřazení listu podle atributu seznamu

output_list = []
for item in range(0, 20):
    print(indexed_chart[item])    