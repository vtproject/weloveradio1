database = 'R1_TEST.sqlite'

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
##	10 "clean_artist_title"	TEXT,
##	11 "day"	INTEGER,
##	12 "month"	INTEGER,
##	13 "year"	INTEGER,
##	14 "days_from"	INTEGER,
##	15 "clean_dj_status"	INTEGER,


#TODO: doplnit datum o číslo tracklistu, vymazat sloupec artist-title, opravit logování  Jingles
# bad words in title - ancestral vision 6.5.

import sqlite3
from bs4 import BeautifulSoup
import requests
import datetime
import re
import logging

update_date = datetime.date.today()   # Datum generování charts / datetime.date(2021, 4, 3)  datetime.date.today() 
execute_date = update_date - datetime.timedelta(1) # Tracklist ze včerejška
tracklist_day = str(execute_date)


bad_words = ["TRACKLIST",
             "ROZHOVOR",
             "SPOTIFY",
             "PLAYLIST",
             "GUESTMIX",
             "KNIŽNÍ",
             "KNIZNI",
             "KULTURN",
             "MIXCLOUD",
             "PALCE",
             "XXX",
             "==",
             "SINGLY",
             "ALBA:",
             "DEGUSTACE",
             "DEGUSTATION DE DESIGN",
             "HODIN",
             "SOUTĚŽ",
             "@",
             "RUBRIKA",
             "PRAVIDELN",
             "ZNELKA",
             "ZNĚLKA",
             "COYS",
             "KOMPILACE",
             "TEA JAY IVO",
             "REGGAE.CZ"]

good_words = ["!!!",
              "18+",
              "2:54",
              "555",
              "813",
              "36",
              "214"] # vyčistit - if = 0

dj_keys = [["BLN","BLN"],
          ["WALTERSTEIN", "DAN WALTERSTEIN"],
          ["SEDLOŇ", "JOSEF SEDLOŇ"],
          ["ŠTEFFL", "JIRKA ŠTEFFL"],
          ["HNYK", "ZDENĚK HNYK"],
          ["KOMÁNKOVÁ", "JANA KOMÁNKOVÁ"],
          ["PIERRE", "PIERRE URBAN"],
          ["ZIMA", "STANISLAV ZIMA"],
          ["KOENIGSMARK", "KRYŠTOF KOENIGSMARK"],
          ["LICHNOVSKÝ", "ZDENĚK LICHNOVSKÝ"],
          ["HAAGER", "TADEÁŠ HAAGER"],
          ["BURIAN", "JIŘÍ BURIAN"],
          ["RŮŽIČKA", "MIKOLÁŠ RŮŽIČKA"],
          ["NEBESÁŘOVÁ","IVETA NEBESÁŘOVÁ"],
          ["LUDVÍKOVÁ", "PETRA LUDVÍKOVÁ"],
          ["MYCLICK", "MYCLICK"],
          ["JEŽKOVÁ", "JANA JEŽKOVÁ"],
          ["KROJIDLO", "MARTIN KROJIDLO"],
          ["ŠTINDL", "ONDŘEJ ŠTINDL"],
          ["VYDRA", "TOMÁŠ VYDRA"],
          ["KOCÁBEK", "TONDA KOCÁBEK"],
          ["NEMRAVOVÁ", "KLÁRA NEMRAVOVÁ"],
          ["TÝC", "FILIP TÝC"],
          ["MAŤKOVÁ", "MAY MAŤKOVÁ"],
          ["ŠTĚRBÁČEK" ,"DAVID ŠTĚRBÁČEK"],
          ["UPPALURI", "RAO UPPALURI"],
          ["ARELLANES" ,"DOUGLAS ARELLANES"],
          ["WLADO" , "WLADO DEL REY"],
          ["ROBERT" ,"ROBERT"],
          ["NITROUS", "NITROUS"],
          ["LISÝ" ,"LIBOR LISÝ"],
          ["STRÝČEK" ,"STRÝČEK MÍŠA"],
          ["VLKOVÁ" ,"KLÁRA VLKOVÁ"],
          ["NAWAR" ,"TOMÁŠ NAWAR"],
          ["SAVALAS" ,"TELLY SAVALAS"],
          ["DUŠEK" ,"JAROSLAV DUŠEK"],
          ["ADAM" ,"VÁCLAV ADAM"],
          ["2K" ,"2K"],
          ["GINGER" ,"GINGER"],
          ["TKÁČ" ,"VOJTĚCH TKÁČ"],
          ["ŽOFIE" ,"ŽOFIE HELFERTOVÁ"],
          ["BAMBAS" ,"ONDŘEJ BAMBAS"],
          ["GADJO" ,"GADJO.CZ"],
          ["PRINCLOVÁ" ,"NICOLE PRINCLOVÁ"],
          ["KAYA" ,"DJ KAYA"],
          ["ULTRAFINO" ,"ULTRAFINO"],
          ["PORATING", "EVA PORATING"],
          ["NOT_ME", "NOT_ME"],
          ["NOVOTNÝ", "TOMÁŠ NOVOTNÝ"],
          ["RÁCHEL", "RÁCHEL"],
          ["KRUML", "JAN KRUML"],
          ["SAVALAS","TELLY SAVALAS"],
          ["JAY", "TEA JAY IVO"],
          ["MIKE.H", "MIKE.H"],
          ["CHONG", "CHONG X"],
          ["TUCO", "TUCO"],
          ["VOJTÍŠEK", "DANIEL VOJTÍŠEK"],
          ["JAN MAREK", "JAN MAREK"],
          ["BRADA", "DAVID BRADA"],
          ["KOSMOS", "RAPHAEL KOSMOS"],
          ["RUDEBOY", "RUDEBOY"],
          ["TUCO", "TUCO"],
          ["C.MONTS", "C.MONTS"],
          ["MIKULÁŠ", "MARTIN MIKULÁŠ"],
          ["KROPÁČEK", "KAREL KROPÁČEK"],
          ["ŠPONER", "JAKUB ŠPONER, PAVEL VÍT"],
          ["HAMMELOVÁ", "LINDA HAMMELOVÁ"],
          ["ABU", "ABU"]]  
  
jingles = [["TÝC", "LEFTFIELD - Original"],
           ["NEMRAV", "LEFTFIELD - Melt"],   
           ["KAYA", "UB40 - The Dance with the devil (Reprise)"],
           ["KAYA", "UB40 - The Dance with the devil"]]
           
def specials_only(input):
    if re.search("[^!█ .:▄/*●><=_1234567890-]", input): #pravda pokud obsahuje i něco jiného než spec.
        return True
    else:
       for s in good_words:
        if input == s:
            return True
    return False

def words(input):
    for s in bad_words:
        bad_word_up = input #oštření velikosti písma - přechod na nový web
        if re.search(s, bad_word_up.upper()) != None:
            return False
    return True

def artist_equal_title(artist, title):
    if artist == title:
        return False
    return True

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

try:
    logger.info("downloading playlists from %s", tracklist_day)
    sqliteConnection = sqlite3.connect(database) 
    
    cursor = sqliteConnection.cursor()
    logger.info("Successfully Connected to db")
    url = "https://www.radio1.cz/program/?date=" + tracklist_day
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser') 
    
    pgm_day = soup.find("div", class_="flex flex-column mr-calc scroller-active")
    
    day_raw_ls = tracklist_day.split("-") 
    day = int(day_raw_ls[2])
    month = int(day_raw_ls[1])
    year = int(day_raw_ls[0])

    f_date = datetime.date(2012, 9, 29) #datum prvního tracklistu v archivu R1
    l_date = datetime.date(year, month, day)
    days_from = l_date - f_date
    days_from = days_from.days    
       
    tracklists = pgm_day.find_all("div", class_="toggle h6 pl1 pr4 line-height-4 overflow-hidden")
    tracklist_counter = 1

    for tracklist in tracklists:
        dj_name = tracklist.find_previous("h4", class_="h4 caps strong")
        dj_name = dj_name.text
        dj_name_upper = dj_name.upper()
        tracklist_item_nr = 1
        tracklist_no = tracklist_day + "_" + str(tracklist_counter)
        
        for dj_key in dj_keys:
            if re.search(dj_key[0], dj_name_upper):
                clean_dj_status = 1            
                clean_tracklist_dj = dj_key[1]
                break
            else:
                clean_dj_status = 0
                clean_tracklist_dj = "-"
                
        if clean_dj_status == 0:
            logger.debug(">Unknown DJ:%s", dj_name)
        else:
            logger.debug(">MATCH DJ:%s", dj_name)

        tracklist_items = tracklist.find_all("li")
        if not tracklist_items:
            logger.debug("   No items in tracklist")
            cursor.execute("""INSERT INTO playlist
     (raw_tracklist_no, raw_tracklist_item_no, raw_tracklist_dj, raw_artist, raw_title,
     clean_artist, clean_title, clean_artist_title, clean_status, clean_tracklist_dj, clean_dj_status, day, month, year, days_from) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (tracklist_no, 0, dj_name, "no_tracklist", "-", "-", "-", "-", 0, clean_tracklist_dj, clean_dj_status, day, month, year, days_from))
 
        for tracklist_item in tracklist_items:        
            raw_artist = (tracklist_item.text.split(" - ", 1)[0])
            raw_title = (tracklist_item.text.split(" - ", 1)[-1])
            if specials_only(raw_artist) is True and words(raw_artist) is True and artist_equal_title(raw_artist, raw_title) is True:
                clean_status = 1
                artist = raw_artist.replace("\"","\'")
                artist = artist.replace("· ","") #vymaznání bulletu na začátku
                artist = artist.upper()
                title = raw_title.replace("\"","\'")
                title = title.title()   
                
                if re.search("SEDLOŇ", dj_name_upper):
                    title = (title.split(" / ")[0])   #Odstranění jména labelu za skladbou    
                    
                artist_title = artist + " - " + title
                logger.debug("   %s %s", tracklist_item_nr, artist_title)
                
                for jingle in jingles:
                    if re.search(jingle[0], dj_name_upper) and artist_title == jingle[1]:
                        clean_status = 0
                        artist = "-"
                        title = "-"
                        artist_title = "-"
                        logger.debug(" X %s %s %s", tracklist_item_nr, raw_artist, raw_title)
                                               
            else:
                clean_status = 0
                artist = "-"
                title = "-"
                artist_title = "-"
                logger.debug(" X %s %s %s", tracklist_item_nr, raw_artist, raw_title)
              
            cursor.execute("""INSERT INTO playlist
     (raw_tracklist_no, raw_tracklist_item_no, raw_tracklist_dj, raw_artist, raw_title,
     clean_artist, clean_title, clean_artist_title, clean_status, clean_tracklist_dj, clean_dj_status, day, month, year, days_from) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (tracklist_no, tracklist_item_nr, dj_name, raw_artist, raw_title, artist, title, artist_title, clean_status, clean_tracklist_dj, clean_dj_status, day, month, year, days_from))
                   
            tracklist_item_nr += 1
        tracklist_counter += 1 
        
    sqliteConnection.commit()
    logger.info("new lines commited")
    cursor.close()
    if sqliteConnection:
        sqliteConnection.close()
        logger.info("connection closed")
      
except sqlite3.Error as error:
    logger.error(error)

    
