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

def decoder(title):
    string = unidecode(title)
    if string == "":
        string = "-"
    return(string)
    
good_words = ["!!!",
              "18+",
              "2:54",
              "555",
              "813",
              "36",
              "214",
              "5:55"]

def specials_only(artist):
    artist = str(artist)
    no_space = artist.replace(" ","")
    if re.search("[^!█ .:▄/*●▶><=_|1234567890-]+", no_space): #pravda pokud obsahuje i něco jiného než spec.
        return(artist)
    else:
        for word in good_words:
            if word in no_space:
                result = artist.split(".")[0]
                break
            else:
                result = "-"
    return(result)
                
bad_strings = ['11-12',
                '10-11',
                 '9-10',
                 '12-01',
                 '01-02',
                 '8-9',
                 '16-17',
                 '6-7',
                 '7-8',
                 '13-14',
                 '17-18',
                 '15-16',
                 '06-07',
                 '18-19',
                 '08-09',
                 '21-22',
                 '19-20',
                 '14-15',
                 '09-10',
                 '12-13',
                 '(17-18)',
                 '07-08',
                 '7-8:',
                 '8-9-',
                 '8-9:',
                 '18.00-19.00',
                 '12-15',
                 '18-19:',
                 '17-17.45',
                 '16.55-18',
                 '15.55-18',
                 '13:30-14',
                 '(23:00-23:45)',
                 '(15-16)',
                 '00-01',
                 '(23:45-00:25)',
                 '9-12',
                 '20-21:',
                 '20-21',
                 '22-20S',
                 "22-20'S",
                 '21-22:',
                 '5.55-07.00',
                 '5.50-7',
                 'F12-01',
                 '1-800',
                 '2-2',
                 '1968-1978',
                 'A.K.A.',
                  '03:00 - 04:00',
                  '9:30',
              "vice info na",
              "info na",
              "vice na"]

def bad_string(artist):
    artist = str(artist)
    for s in bad_strings:
        artist = artist.replace(s, "")
    return(artist)


del_artist_after = [" FEAT",
             " FT ",
             " FT: ",
             " FT."]

def del_artist_after_string(artist):
    for s in del_artist_after:
        artist = artist.split(s)[0]  
    return(artist)   

del_title_after = [" feat",
             " ft ",
             " ft: ",
             " ft.",
             "(",
             "[",
             "{"]

def del_title_after_string(artist):
    for s in del_title_after:
        artist = artist.split(s)[0]  
    return(artist) 


to_space = ['.',
            '+',
            '&',
            ',',
            '/',
            '-',
            '_',
            '(',
            ')',
            '*',
            '#',
            '[',
            ']',
            '?',
            '"',
            '>',
            '<',
            '|',
            '=',
            '_',
            '{',
            '~', 
            '^', 
            ';', 
            '%', 
            '}',
            '\\']

def char_to_space(artist):
    for s in to_space:
        artist = artist.replace(s, " ")
    return(artist) 
    
replace = [["THE THE", "THETHE"],
           ["4HERO", "4 HERO"],
           ["808STATE", "808 STATE"],
           ["'", ""],
           ["`", ""],
           [":", ""]]

def replace_string(artist):
    for pair in replace:
        artist = artist.replace(pair[0], pair[1])
    return(artist)

bad_lines = ["TRACKLIST",
             "ROZHOVOR",
             "SPOTIFY",
             "PLAYLIST",
             "GUESTMIX",
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
             "SOUTEZ",
             "@",
             "RUBRIKA",
             "PRAVIDELN",
             "ZNELKA",
             "COYS",
             "KOMPILACE",
             "TEA JAY",
             "REGGAE.CZ",
             "BANDCAMP",
             "GMAIL",
             "FB & IG",
             "HTTP",
             "NO_TRACKLIST",
             "GUEST MIX",
             "SEANCE",
             "SEANCI",
             "DNESNI",
             "\t\t\t\t\t00",
             "ZPRAVODAJSTVÍ",
             "INTERVIEW",
             "ZPRAVODAJSTV",
             "5 DNI S"]

def bad_line(artist):
    for word in bad_lines:
        if word in artist:
            return("-")
            break
    return(artist)

bad_words_artist =["THE",
            "AND",
            "OF",
            "DE",
            "LA",
            "IN",
            "WITH",
            "HIS",
            "ON",
            "LE",
            "TO",
            "IS",
            "AKA",
           "SOUTEZ",
           "VS",
           "V"]

def five_words_artist(artist):    
    artist = [word for word in artist.split() if word not in bad_words_artist]

    if len(artist) < 5:
        for x in range(len(artist),5):
            artist.append("-")

    artist = artist[0:5]        
    artist = " ".join(artist)
    return(artist) 


bad_words_title =["the",
            "a",
            "of",
            "to",
            "is",
            "it",
           "http",
           "https",
           "www"]

def five_words_title(artist):    
    artist = [word for word in artist.split() if word not in bad_words_title]

    if len(artist) < 5:
        for x in range(len(artist),5):
            artist.append("-")

    artist = artist[0:5]        
    artist = " ".join(artist)
    return(artist)

jingles = [["FILIP TÝC", "LEFTFIELD - - - -original - - - -"],
           ["KLÁRA NEMRAVOVÁ", "LEFTFIELD - - - -melt - - - -"],   
           ["DJ KAYA", "UB40 - - - -dance with devil - -"],
           ["ANCESTRAL VISION & NOTSUREYET", "ANCESTRAL VISION - - -ANCESTRAL VISION - - -"]] 

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
          ["NEBES","IVETA NEBESÁŘOVÁ"],
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
          ["ANCESTRAL", "ANCESTRAL VISION & NOTSUREYET"],
          ["SYROVÝCH", "PETR VRBA & VOJTĚCH STANĚK"],
          ["PAŘÍZEK", "MICHAL PAŘÍZEK"],
          ["SAKU", "SAKU"],
          ["SLEEPCLUBBING", "JANA KOMÁNKOVA"],
          ["ABU", "ABU"],
          ["MARIANA", "MARIANA HRADILKOVÁ"]]  

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
    
def clean_artist(artist):
    artist = str(artist)
    artist = artist.upper()
    artist = decoder(artist)
    artist = specials_only(artist)
    artist = bad_string(artist)
    artist = del_artist_after_string(artist)
    artist = char_to_space(artist)
    artist = replace_string(artist)
    artist = bad_line(artist)
    artist = five_words_artist(artist)
    return(artist)
    
def clean_title(title):
    title = str(title)
    title = title.lower()
    title = decoder(title)
    title = specials_only(title)
    title = bad_string(title)
    title = del_title_after_string(title)
    title = char_to_space(title)
    title = replace_string(title)
    title = bad_line(title)
    title = five_words_title(title)
    return(title)
    
try:
    connection = sqlite3.connect('weloveradio1db_D.sqlite') 
    cursor = connection.cursor()
    sql_select_query = """SELECT * from playlist where id = ?"""
    sql_clean_artist_query = """UPDATE playlist SET clean_artist = ? where id = ?"""
    sql_clean_title_query = """UPDATE playlist SET clean_title = ? where id = ?"""
    sql_clean_status_query = """UPDATE playlist SET clean_status = ? where id = ?"""
    sql_clean_dj_status_query = """UPDATE playlist SET clean_dj_status = ? where id = ?"""
    sql_clean_tracklist_dj_query = """UPDATE playlist SET clean_tracklist_dj = ? where id = ?"""
    
    cursor.execute("""SELECT * from sqlite_sequence where name = "playlist" """)
    sql_rows = cursor.fetchone()
    last_row = int(sql_rows[1])+1
    print("Cleanng up to ", last_row) 
    
    count = 0
    for row_id in range(1, last_row): 
        cursor.execute(sql_select_query, (row_id,))
        record = cursor.fetchone()
                        
        clartist = clean_artist(record[4])
        cltitle = clean_title(record[5])
                         
        cursor.execute(sql_clean_artist_query, (clartist, row_id))
        cursor.execute(sql_clean_title_query, (cltitle, row_id))
        
        if clartist == "- - - - -":
            cursor.execute(sql_clean_status_query, (0, row_id))
        else:
            cursor.execute(sql_clean_status_query, (1, row_id))
        
        
        raw_dj = record[3]
        if not raw_dj:
            raw_dj = "-"
        
        for dj_key in dj_keys:
            if re.search(dj_key[0], raw_dj.upper()):
                cursor.execute(sql_clean_dj_status_query, (1, row_id))           
                cursor.execute(sql_clean_tracklist_dj_query, (dj_key[1], row_id))
                break
            else:
                cursor.execute(sql_clean_dj_status_query, (0, row_id))
                cursor.execute(sql_clean_tracklist_dj_query, ("-", row_id))
                
        artist_title = clartist + cltitle
        
        clean_dj = record[7]
        if not clean_dj: 
            clean_dj = "-"
                
        for jingle in jingles:
            if re.search(jingle[0], clean_dj) and artist_title == jingle[1]:
                cursor.execute(sql_clean_status_query, (0, row_id))
                break

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
