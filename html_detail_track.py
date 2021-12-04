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
        
def month_back(artist, title, actual_day):
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
    return(record)
    cursor.close()
    
def past_month(artist, title, actual_day):
    to_day = actual_day - 6
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
    return(record)
    cursor.close()


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

def main(artist, title, detail_name, actual_day):        
    try:
        update_date = datetime.date.today()

        record = month_back(artist, title, actual_day)
        record_past_list =  past_month(artist, title, actual_day)
        
        
        # logger.info("starting html generator from %s", landscape_data[0]) 
        
        file_name = landscape_data[1] + "track_detail_" + detail_name + ".html"
        
        file_details = open(file_name, "w") #delete previous test file 
        file_details.close()
        file_details = open(file_name, "a", encoding = "utf-8")

        
        html_header =("""<!DOCTYPE html>
    <html lang="cs">
    <head>
    <meta charset="UTF-8">
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-135284242-1"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'UA-135284242-1');
    </script>
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-MFMPT2T');</script>
    <!-- End Google Tag Manager -->
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>co nejvíc hraje Radio 1</title>
    <link rel="stylesheet" href="w3_third.css">
    </head>
    <body>
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MFMPT2T"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager (noscript) -->
    <div class="w3-container w3-red">
      <h1>co nejvíc hraje <a href="https://www.radio1.cz/" target="_blank"><U>Radio 1</U></a></h1>
      <a href="changelog.html"><U>info / changelog</U></a>&nbsp; &nbsp; &nbsp; <a href="https://github.com/vtproject/weloveradio1" target="_blank"><U>GitHub</U></a>&nbsp; &nbsp; &nbsp;&nbsp;aktualizace:&nbsp;""" + date_out(update_date) + """<br>
      <br>
    </div>""")

        html_menu_details =("""<div class="w3-container">
      <h4>| <a href = "tracks.html"><U>nejhranější skladby</U></a> |&nbsp;<a href = "artists.html"><U>nejhranější&nbsp;skupiny</U></a>&nbsp;|<br>
    | <a href = "djs.html"><U>žebříčky podle moderátorů</U></a> |<a href = "index.html">&nbsp;<U>novinky&nbsp;týdne</U>&nbsp;|&nbsp;<br>
    <br>
    <a href = "tracks.html">&#60; <U>zpět na nehranější skladby</U><br><br></a></h4> 
    </div>
    <div class="w3-container"  style="max-width:600px">
    """)
    
        html_track_title =("""Detail skladby <b>""" + artist + """ - """ + title + """</b>:<br><br>\n""")
        html_track_info =("""<b>Skladbu hráli v minulém měsíci:</b><br><br>\n""")
        html_past_list_info = ("""<br><b>Dříve skladbu hráli:</b><br><br>\n""")
        html_nikdo = ("""<br><b>Dříve ještě nikdo skladbu nehrál.</b><br>\n""")
        html_nikdo_v_mesici = ("""<b>Skladbu v minulém měsící nikdo nehrál.</b></br>\n""")
        
        artisttitle = artist + " - " + title
          
        import youtube_embed
        target_part = youtube_embed.main(artisttitle)
        # target_part = "bXrc7w0Yffg" # pro testování - nespouští se youtube scrap
        
        html_youtube_embed = '<div class="video-container"><iframe src="https://www.youtube.com/embed/' + target_part + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"></iframe> </div> <br>\n'        
                
        file_details.write(html_header)
        file_details.write(html_menu_details)
        file_details.write(html_track_title)
        file_details.write(html_youtube_embed)
        

        
        if not record:
            file_details.write(html_nikdo_v_mesici)
        else:
            file_details.write(html_track_info)
            for detail_row in record:
                if detail_row[0] is None:
                    dj = "Neznámý DJ"
                elif detail_row[0] == "-":
                    dj = "Neznámý DJ"
                else:
                    dj = str(detail_row[0])
                detail_row_out = str(detail_row[1]).zfill(2) + "." + str(detail_row[2]).zfill(2) + "." + str(detail_row[3]) + " : " + dj + "<br>\n"
                file_details.write(detail_row_out)


        if not record_past_list:
            file_details.write(html_nikdo)
        else:
            file_details.write(html_past_list_info) 
            
            for detail_row in record_past_list:
                if detail_row[0] is None:
                    dj = "Neznámý DJ"
                elif detail_row[0] == "-":
                    dj = "Neznámý DJ"
                else:
                    if detail_row[1] < 10:
                        detail_row_out = "&nbsp;&nbsp;" + str(detail_row[1]) + " x " + str(detail_row[0]) + "<br>\n"
                    else:
                        detail_row_out = str(detail_row[1]) + " x " + str(detail_row[0]) + "<br>\n"
                        
                file_details.write(detail_row_out)
        
        first_play = dj_first_play(artist, title, actual_day)
        
        if detail_row[0] is None:
            dj = "Neznámý DJ"
        elif detail_row[0] == "-":
            dj = "Neznámý DJ"
        else:
            dj = str(detail_row[0])
                
        first_play_out =("""<br><b>Skladbu od října 2012 poprvé hrál/a:</b><br><br>""" + 
                         str(first_play[1]).zfill(2) + "." + str(first_play[2]).zfill(2) + "." + 
                         str(first_play[3]) + " : " + dj + """<br>\n""")
        file_details.write(first_play_out)
            
        html_end = ("""</div>
       <br>
       <br>
    </body>
    </html>""") 
        file_details.write(html_end)
        file_details.close()
        
    except sqlite3.Error as error:
        logger.error("Failed:%s", error)


# main("MINISTRY", "Good Trouble", "_test", 3352)
# main("ARLETA", "Statement", "_test", 3352)
# main("OVERMONO", "Diamond Cut", "_test", 3352)  
# main("WARPAINT", "Love Is To Die", "_test", 3352)
# main("FLOEX", "Drama Queen", "_test", 3352)