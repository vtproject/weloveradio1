import sqlite3
import datetime
import re
import logging
import news_chart
import youtube_embed

def date_out(datum):
    date_out_f = str(datum)
    date_out_f = datetime.datetime.strptime(date_out_f, '%Y-%m-%d')
    date_out_f = date_out_f.strftime('%#d.%#m.%Y')
    return date_out_f

def djs_week_back(artist, title, actual_day):

    to_day = actual_day
    from_day = actual_day - 6
    
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
        return(record)    

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
    landscape_data = ["weloveradio1db_P.sqlite", "html_P/tracks.html", "html_P/artists.html", "html_P/djs.html", "html_P/index.html"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1db_T.sqlite", "html_T/tracks.html", "html_T/artists.html", "html_T/djs.html", "html_T/index.html"]
else:
    landscape_data = ["weloveradio1db_D.sqlite", "html_D/tracks.html", "html_D/artists.html", "html_D/djs.html", "html_D/index.html"]

connection = sqlite3.connect(landscape_data[0])
        
paragraph_count = 0

update_date = datetime.date.today() # Datum generování datetime.date(2021, 4, 3)  datetime.date.today() 
execute_date = update_date - datetime.timedelta(1) # Datum generování html  

actual_day = execute_date - datetime.date(2012, 9, 29)
actual_day = actual_day.days
try:
    logger.info("starting news html generator from %s", landscape_data[0]) 
    
    file_news = open(landscape_data[4], "w") #delete previous test file 
    file_news.close()

    file_news = open(landscape_data[4], "a", encoding = "utf-8")
    
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
    file_news.write(html_header)
    
    html_menu_news =("""<div class="w3-container">
  <h4>| <a href = "tracks.html"><U>nejhranější skladby</U></a> |&nbsp;<a href = "artists.html"><U>nejhranější&nbsp;skupiny</U></a>&nbsp;|<br>
| <a href = "djs.html"><U>žebříčky podle moderátorů</U></a> |&nbsp;<b>novinky&nbsp;týdne&nbsp;</b>|</h4> 
</div>
""")
    file_news.write(html_menu_news)
    
    from_day = actual_day - 6
    to_day = actual_day
    
    chart_lists_news = news_chart.main(from_day, to_day)
    
    paragraph_count = 0
    
    from_day_out = datetime.date(2012, 9, 29) + datetime.timedelta(from_day)
    to_day_out = datetime.date(2012, 9, 29) + datetime.timedelta(to_day)
    
    html_list_dates_news =("""<div class="w3-container">
    <h2> týden """ + date_out(from_day_out) + """ - """ + date_out(to_day_out) + """</h2>
  </div>
<div class="w3-row-padding">  
""")
    file_news.write(html_list_dates_news)
    
    for chart_list in chart_lists_news:            
        
        record = djs_week_back(chart_list[0], chart_list[1], actual_day)
        dj_check = []
        for item in record:
            dj_check.append(item[0])
        
        if not all(x == dj_check[0] for x in dj_check): 
        
            html_video_header = (""" <div class="w3-third">
     <b>""" + chart_list[0] + """ - """ + chart_list[1] + """</b><br>\n""")
            
            file_news.write(html_video_header)
            
            artisttitle = chart_list[0] + " - " + chart_list[1]
            target_part = youtube_embed.main(artisttitle)
            # target_part = "bXrc7w0Yffg" # pro testování - nespouští se youtube scrap
            
            html_youtube_embed = ('<div class="video-container">\n<iframe src="https://www.youtube.com/embed/' + target_part + 
                                  '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"></iframe></div><br>\n')        
            
            file_news.write(html_youtube_embed)
            
            file_news.write("Skladbu poprvé hráli:<br>")
            
            
            
            for detail_row in record:
                if detail_row[0] is None:
                    dj = "Neznámý DJ"
                elif detail_row[0] == "-":
                    dj = "Neznámý DJ"
                else:
                    dj = str(detail_row[0])
                detail_row_out = str(detail_row[1]).zfill(2) + "." + str(detail_row[2]).zfill(2) + "." + str(detail_row[3]) + " : " + dj + "<br>\n"
                file_news.write(detail_row_out)
            
            paragraph_count += 1

            if paragraph_count == 3:
                html_break2 =("""
           <br>
           <br>
         </div>  
      </div>
      <div class="w3-row-padding">
    """)
                file_news.write(html_break2)
                paragraph_count = 0            
            else:
                html_break1 = ("""     
           <br>
           <br>
      </div>
    """)
                file_news.write(html_break1)
                
            print("█", end = "", flush=True) #monitor    
    print("\n")
    html_end = ("""</div>
<div class="w3-container w3-red">
  <br>
</div>
</body>
</html>""")     
    
    file_news.write(html_end)
    file_news.close()
    
 
except sqlite3.Error as error:
    logger.error("Failed:%s", error)
finally:
    if connection:
        connection.close()
        logger.info("file %s generated", landscape_data[4])
        # logger.info("db %s closed", landscape_data[0])


