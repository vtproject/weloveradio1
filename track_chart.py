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

def count_limit(from_day, to_day, days_back):
    
    from_day = from_day - days_back
    to_day = to_day - days_back
    
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_artist, clean_title, COUNT(clean_title)
    FROM
        playlist
    WHERE clean_status = 1 AND days_from BETWEEN ? AND ?
    GROUP BY
        clean_artist, clean_title
    HAVING
        COUNT(clean_title) > 1
    ORDER BY
        COUNT(clean_title) DESC,
        clean_artist ASC
    LIMIT 20;
    """, (str(from_day), str(to_day)))
      
    chart_unsorted = cursor.fetchall()
    cursor.close()
    
    if (len(chart_unsorted)) < 20:
        if (len(chart_unsorted)) == 0:
            return(0)    
        return(chart_unsorted[-1][2])
    else:    
        return(chart_unsorted[19][2])


def retrieve_chart_tracks(from_day, to_day, limit, days_back):
    
    if limit == -1:
        return([])
    else:
        from_day = from_day - days_back
        to_day = to_day - days_back
        
        cursor = connection.cursor()
        cursor.execute("""
        SELECT
            clean_artist, clean_title, COUNT(clean_title)
        FROM
            playlist
        WHERE clean_status = 1 AND days_from BETWEEN ? AND ?
        GROUP BY
            clean_artist, clean_title
        HAVING
            COUNT(clean_title) > ?    
        ORDER BY
            COUNT(clean_title) DESC,
            clean_artist ASC;
        """, (str(from_day), str(to_day), limit))
        return(cursor.fetchall())
        cursor.close()
    

def track_index(artist, title):
 
    try:
          
        if (artist == "-" and title == "-"):
            djindex = 0
            track_play_index = 0
            time_diff_index = 0
            artist_play_index = 0
        else:
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
            if len(timediff) == 0:
                time_diff_index = 0
            else:    
                time_diff_index=(sum(timediff)/len(timediff)) #průměrný počet dní mezi hraním skladby   
            if time_diff_index == 0:
                time_diff_index = 2 #nereálné zobrazení v detailu skladby
            else:
                time_diff_index = 1/time_diff_index 
            
            return([djindex, track_play_index, time_diff_index, artist_play_index])
     
        
    except sqlite3.Error as error:
        logger.error("Failed:%s", error)

def indexed_chart(from_day, to_day, days_back):
    limit = count_limit(from_day, to_day, days_back)-1
    chart = retrieve_chart_tracks(from_day, to_day, limit, days_back)
    
    
    indexed_chart = []
    cnt = 1
    for track in chart:
        raw_index = track_index(track[0], track[1])
        index = (str(track[2]).zfill(3) + "." + #počet přehrání skladby v období
                 str(raw_index[0]).zfill(2) + "." + #počet djs celkem, kteří skladbu hráli
                 str(raw_index[1]).zfill(3) + "." + #počet přehrání skladby celkem
                 str(math.trunc(raw_index[2]*1000)).zfill(4) + "." + #převrácená hodnota průměrné četnosti hraní skladby ve dnech
                 str(raw_index[3]).zfill(4)) #počet přehrání skupiny celkem
        indexed_chart.append([index, track[0], track[1], track[2], raw_index[0], raw_index[1], round(1/raw_index[2], 1), raw_index[3]])
        i = (cnt/len(chart))*100
        print('Processing %i%%\r'%i, end="") #zobrazení procenta
        cnt+=1
    print()
    indexed_chart.sort(key=operator.itemgetter(0), reverse = True) #seřazení listu podle atributu seznamu
    
    if len(indexed_chart) < 20:
        for x in range(0,20-len(indexed_chart)):
            indexed_chart.append(["0", "-", "", "", "", "", "", "", ""])

      
    indexed_chart = indexed_chart[0:20]
    
    cnt = 1    
    for item in range(0,20):
        indexed_chart[item].append(cnt) #přidání čísla pořadí v žebříčku
        cnt+=1
    
    return(indexed_chart)        

def main(from_day, to_day):       
    # chart = indexed_chart(from_day, to_day, 0)
    # chart_last = indexed_chart(from_day, to_day, 1)
    
    # chart_out = []
    
    # for track in chart:
        # arrow = "*&nbsp;"
        # if (track[1] == "-" and track[2] == ""):
            # arrow = "&nbsp;&nbsp;"
        # else:
            # for track_last in chart_last:
                # if (track[1] == track_last[1] and track[2] == track_last[2]):
                    # if track[3] > track_last[3]:
                        # arrow = "&uarr;&nbsp;" 
                    # elif track[3] < track_last[3]:
                        # arrow = "&darr;&nbsp;" 
                    # else:
                        # arrow = "&nbsp;&nbsp;"
                    # break
        # chart_out.append([arrow, track[1], track[2], track[3], track[4], track[5], track[6], track[7]])
    # return(chart_out)
    return([['&nbsp;&nbsp;', 'ARLETA', 'Statement', 4, 4, 4, 0.3, 34], ['&nbsp;&nbsp;', 'MINISTRY', 'Good Trouble', 3, 9, 12, 11.9, 142], ['&nbsp;&nbsp;', 'BADFOCUS', 'Defy', 3, 6, 12, 41.5, 34], ['&darr;&nbsp;', 'JACK WHITE', 'Taking Me Back', 3, 6, 8, 4.0, 356], ['&nbsp;&nbsp;', 'DUNCAN FORBES', 'The Next Step', 3, 3, 3, 1.0, 9], ['&nbsp;&nbsp;', 'OTIK', 'Lightyear Dub', 3, 3, 3, 1.5, 51], ['&nbsp;&nbsp;', 'OVERMONO', 'Bby', 3, 3, 3, 1.5, 46], ['&nbsp;&nbsp;', 'HVOB', 'Bruise', 3, 3, 3, 2.5, 471], ['&nbsp;&nbsp;', 'MODERAT', 'Bad Kingdom', 2, 28, 125, 25.7, 889], ['&nbsp;&nbsp;', 'BICEP', 'Atlas', 2, 12, 41, 18.0, 350], ['&nbsp;&nbsp;', 'ARAB STRAP', 'The Turning Of Our Bones', 2, 9, 26, 21.8, 55], ['&nbsp;&nbsp;', 'PERFUME GENIUS', 'Describe', 2, 9, 13, 53.2, 212], ['&nbsp;&nbsp;', 'AMELIE SIBA', 'Ljubljana', 2, 9, 11, 2.8, 119], ['&nbsp;&nbsp;', 'TENNIS', 'Need Your Love', 2, 8, 16, 44.7, 201], ['&nbsp;&nbsp;', 'SPIRITUALIZED', 'Always Together With You', 2, 8, 8, 2.9, 126], ['&nbsp;&nbsp;', 'GREG DULLI', 'It Falls Apart', 2, 7, 15, 45.5, 34], ['&nbsp;&nbsp;', 'BLACK MARBLE', 'Somewhere', 2, 7, 12, 9.5, 82], ['&nbsp;&nbsp;', 'GRANDBROTHERS', 'Organism', 2, 7, 11, 30.8, 120], ['&nbsp;&nbsp;', 'BILLIE EILISH', 'Oxytocin', 2, 6, 11, 11.2, 211], ['*&nbsp;', 'TOMÁŠ TKÁČ', 'Ale/Jestli', 2, 5, 8, 80.3, 27]])    
