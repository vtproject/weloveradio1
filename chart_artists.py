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
            calc_artist, COUNT(calc_artist)
        FROM   (SELECT
            calc_artist
        FROM
            playlist
        WHERE clean_status = 1 AND days_from BETWEEN ? AND ?
        GROUP BY
            calc_artist, raw_tracklist_no)
        GROUP BY 
            calc_artist
        HAVING
            COUNT(calc_artist) > 1    
        ORDER BY
            COUNT(calc_artist) DESC,
            calc_artist ASC
    LIMIT 20;
    """, (str(from_day), str(to_day)))
      
    chart_unsorted = cursor.fetchall()
    cursor.close()
    
    if (len(chart_unsorted)) < 20:
        if (len(chart_unsorted)) == 0:
            return(0)    
        return(chart_unsorted[-1][1])
    else:    
        return(chart_unsorted[19][1])
    

def retrieve_chart(from_day, to_day, limit, days_back):

    if limit == -1:
        return([])
    else:
        from_day = from_day - days_back
        to_day = to_day - days_back
        
        cursor = connection.cursor()
        cursor.execute("""
        SELECT
            calc_artist, COUNT(calc_artist)
        FROM   (SELECT
            calc_artist
        FROM
            playlist
        WHERE clean_status = 1 AND days_from BETWEEN ? AND ?
        GROUP BY
            calc_artist, raw_tracklist_no)
        GROUP BY 
            calc_artist
        HAVING
            COUNT(calc_artist) > ?    
        ORDER BY
            COUNT(calc_artist) DESC,
            calc_artist ASC;
        """, (str(from_day), str(to_day), limit))
        return(cursor.fetchall())
        cursor.close()
        

def artist_index(artist):
 
    try:
          
        if artist == "-":
            djindex = 0
            artist_play_index = 0
            time_diff_index = 0
            track_play_index = 0
        else:
            cursor = connection.cursor()
            cursor.execute("""
            SELECT
                clean_tracklist_dj, days_from
            FROM
                playlist
            WHERE calc_artist = ? 
            ORDER BY
                days_from DESC;
            """, (artist,))
            
            artist_record = cursor.fetchall()
            cursor.close()
            
            cursor = connection.cursor()
            cursor.execute("""
            SELECT
                clean_title
            FROM
                playlist
            WHERE calc_artist = ?
            GROUP BY
                clean_title;            
            """, (artist,))
            
            tracks_record = cursor.fetchall()
            cursor.close()
            
            djindex = len(set([item[0] for item in artist_record])) #počet djs, kteří skladbu hráli celkem
            artist_play_index = len(artist_record) #počet hraní skaladby celkem
            tracks_play_index = len(tracks_record) #počet skladeb od skupiny celkem
            
            timediff=[]
            for item in range(0,len(artist_record)-1):
                timediff.append(artist_record[item][1] - artist_record[item+1][1])
            if len(timediff) == 0:
                time_diff_index = 0
            else:    
                time_diff_index=(sum(timediff)/len(timediff)) #průměrný počet dní mezi hraním skladby   
            if time_diff_index == 0:
                time_diff_index = 2 #nereálné zobrazení v detailu skladby
            else:
                time_diff_index = 1/time_diff_index 
            
            return([djindex, artist_play_index, time_diff_index, tracks_play_index])
     
        
    except sqlite3.Error as error:
        logger.error("Failed:%s", error)

def indexed_chart(from_day, to_day, days_back):
    limit = count_limit(from_day, to_day, days_back)-1
    chart = retrieve_chart(from_day, to_day, limit, days_back)
    
    
    indexed_chart = []
    cnt = 1
    for track in chart:
        raw_index = artist_index(track[0])
        index = (str(track[1]).zfill(4) + "." + #počet přehrání skupiny v období
                 str(raw_index[0]).zfill(2) + "." + #počet djs celkem, kteří skupinu hráli
                 str(raw_index[1]).zfill(4) + "." + #počet přehrání skupiny celkem
                 str(math.trunc(raw_index[2]*1000)).zfill(4) + "." + #převrácená hodnota průměrné četnosti hraní skupiny ve dnech
                 str(raw_index[3]).zfill(4)) #počet skladeb od skupiny celkem
        indexed_chart.append([index, track[0], track[1]])
        i = (cnt/len(chart))*100
        print('Processing %i%%\r'%i, end="") #zobrazení procenta
        cnt+=1
    print()
    indexed_chart.sort(key=operator.itemgetter(0), reverse = True) #seřazení listu podle atributu seznamu
    
    if len(indexed_chart) < 20:
        for x in range(0,20-len(indexed_chart)):
            indexed_chart.append(["0", "-", "", ""])

    indexed_chart = indexed_chart[0:20]
    
    cnt = 1    
    for item in range(0,20):
        indexed_chart[item].append(cnt) #přidání čísla pořadí v žebříčku
        cnt+=1
    return(indexed_chart)        

def main(from_day, to_day):  
    chart = indexed_chart(from_day, to_day, 0)
    chart_last = indexed_chart(from_day, to_day, 1)
    
    chart_out = []
    
    for track in chart:
        arrow = "*&nbsp;"
        if track[1] == "-":
            arrow = "&nbsp;&nbsp;"
        else:
            for track_last in chart_last:
                if track[1] == track_last[1]:
                    if track[2] > track_last[2]:
                        arrow = "&uarr;&nbsp;" 
                    elif track[2] < track_last[2]:
                        arrow = "&darr;&nbsp;" 
                    else:
                        arrow = "&nbsp;&nbsp;"
                    break
        chart_out.append([arrow, track[1], track[2], track[3], track[0]])
    return(chart_out)
    # return([['&nbsp;&nbsp;', 'THE WAR ON DRUGS', 'Wasted', 4], ['&nbsp;&nbsp;', 'DÝM', 'Andělský Tornádo', 4],
    # ['&nbsp;&nbsp;', 'ISLAND MINT', 'Suburbs', 2], ['&nbsp;&nbsp;', 'AIKO', 'Gemini', 2],
    # ['&nbsp;&nbsp;', 'JACK WHITE', 'Taking Me Back', 2], ['&nbsp;&nbsp;', 'GEORGE FITZGERALD', 'Ultraviolet', 2],
    # ['&darr;&nbsp;', 'VISION OF 1994', 'Code Isolation', 2], ['&darr;&nbsp;', 'ARLETA', 'Statement', 2],
    # ['&darr;&nbsp;', 'HVOB', 'Bruise', 2], ['&darr;&nbsp;', 'BEACH HOUSE', 'Superstar', 2], ['&nbsp;&nbsp;', 'BIG THIEF', 'Time Escaping', 2],
    # ['&nbsp;&nbsp;', 'HOMEOFFICE', 'Solitude', 2], ['&nbsp;&nbsp;', 'SOFT KILL', 'Bully', 2], ['&nbsp;&nbsp;', 'BEATFOOT', 'Green', 2],
    # ['&nbsp;&nbsp;', '100 GECS', 'Mememe', 2], ['*&nbsp;', 'YUMI ZOUMA', 'Mona Lisa', 2], ['*&nbsp;', '1010 BENJA SL', 'High', 2],
    # ['*&nbsp;', 'FRED AGAIN..', 'Faisal (Envelops Me)', 2], ['*&nbsp;', 'JITWAM & COSMO´S MIDNIGHT', 'Feel Good', 2],
    # ['*&nbsp;', 'ALEX CAMERON', 'Sara Jo', 2]]) 