import sqlite3
import datetime
import urllib.parse
import re
import logging
import html_detail_track
import html_detail_artist
import cover_download
import chart_artists
import chart_tracks

def date_out(datum):
    date_out_f = str(datum)
    date_out_f = datetime.datetime.strptime(date_out_f, '%Y-%m-%d')
    date_out_f = date_out_f.strftime('%#d.%#m.%Y')
    return date_out_f

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
    landscape_data = ["weloveradio1db_P.sqlite", "html_P/tracks.html", "html_P/artists.html", "html_P/djs.html"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1db_T.sqlite", "html_T/tracks.html", "html_T/artists.html", "html_T/djs.html"]
else:
    landscape_data = ["weloveradio1db_D.sqlite", "html_D/tracks.html", "html_D/artists.html", "html_D/djs.html"]

connection = sqlite3.connect(landscape_data[0])
        
update_date = datetime.date.today() # Datum generování datetime.date(2021, 4, 3)  datetime.date.today() 
execute_date = update_date - datetime.timedelta(1) # Datum generování html  

actual_day = execute_date - datetime.date(2012, 9, 29)
actual_day = actual_day.days
print(actual_day)
days_back = [6, 30, 182, 364, 1824, 3650]
chart_name = ["za minulý týden", "za minulý měsíc", "za minulých 6 měsíců", "za minulý rok", "za minulých 5 let", "za minulých 10 let"]
chart_period = ["v minulém týdnu", "v minulém měsíci", "v minulých 6 měsících", "v minulém roce", "v minulých 5 letech", "v minulých 10 letech"]

def main(html_switch):
    try:
        paragraph_count = 0
        
        logger.info("starting html generators from %s", landscape_data[0]) 
        
        if html_switch == "tracks":
            file = open(landscape_data[1], "w") #delete previous test file 
            file.close()
            file = open(landscape_data[1], "a", encoding = "utf-8") 
            
            detail_name = "track_detail_"
            
        elif html_switch == "artists":    
            file = open(landscape_data[2], "w") 
            file.close()
            file = open(landscape_data[2], "a", encoding = "utf-8")  

            detail_name = "artist_detail_"            
        
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
        file.write(html_header)
        
        if html_switch == "tracks":
            html_menu =("""<div class="w3-container">
          <h4>| <b>nejhranější skladby</b> |&nbsp;<a href = "artists.html"><U>nejhranější&nbsp;skupiny</U></a>&nbsp;|<br>
        | <a href = "djs.html"><U>žebříčky podle moderátorů</U></a> |<a href = "index.html">&nbsp;<U>novinky&nbsp;týdne</U></a>&nbsp;|</h4> 
        </div>
        <div class="w3-row-padding">
        """)
        elif html_switch == "artists":
            html_menu =("""<div class="w3-container">
          <h4>| <a href = "tracks.html"><U>nejhranější skladby</U></a> |&nbsp;<b>nejhranější&nbsp;skupiny</b>&nbsp;|<br>
        | <a href = "djs.html"><U>žebříčky podle moderátorů</U></a> |<a href = "index.html">&nbsp;<U>novinky&nbsp;týdne</U></a>&nbsp;|</h4> 
        </div>
        <div class="w3-row-padding">
        """)
    
        file.write(html_menu)
            
        detail_number_1 = 1
            
        for chart_no in range(0,6):            
            
            chart_no_monitor = chart_no + 1
                    
            if actual_day - days_back[chart_no] < 1:
                from_day = 0
            else:
                from_day = actual_day - days_back[chart_no]

            to_day = actual_day

            from_day_out = datetime.date(2012, 9, 29) + datetime.timedelta(from_day)
            to_day_out = datetime.date(2012, 9, 29) + datetime.timedelta(to_day)
           
            html_list_dates =("""  <div class="w3-third">
        <h2><b> """+ chart_name[chart_no] + """</b> (""" + date_out(from_day_out) + """ - """ + date_out(to_day_out) + """) </h2>  
    """)
            file.write(html_list_dates) 
            
            if html_switch == "tracks":
                chart_list = chart_tracks.main(from_day, to_day) # external chart
            elif html_switch == "artists":    
                chart_list = chart_artists.main(from_day, to_day)
                   
            detail_number_2 = 1

            for item in range(0,20):
                
                if html_switch == "tracks":
                    item_name = chart_list[item][1] + ' - ' + chart_list[item][2]
                    no_of_plays = str(chart_list[item][3])
                
                elif html_switch == "artists": 
                    item_name = chart_list[item][1]
                    no_of_plays = str(chart_list[item][2])
       
                if chart_list[item][1] == "-":
                    html_list = '        <li> -</li>\n' 
                else:
                    detail_file_number = str(detail_number_1).zfill(2) + "_" + str(detail_number_2).zfill(2)                 
                    
                    html_list =( '        <li><span style="color:red">' + chart_list[item][0] + 
                                        '</span><a href = "' + detail_name + detail_file_number + 
                                        '.html">' + item_name +
                                        ' <img src="link.png" width="10" height="10"></a> (' + no_of_plays +
                                        ')</li>\n')
                                        
                    html_list_bold = ('        <li><span style="color:red">' + chart_list[item][0] +  
                                             '</span><a href = "' + detail_name + detail_file_number + 
                                             '.html"><b>' + item_name + 
                                             '</b> <img src="link.png" width="10" height="10"></a> (' + no_of_plays +
                                             ')</li>\n')

                    if html_switch == "tracks":
                        html_detail_track.main(str(chart_list[item][1]),
                                              str(chart_list[item][2]),
                                              detail_file_number,
                                              actual_day)
                    
                    elif html_switch == "artists":
                        html_detail_artist.main(str(chart_list[item][1]),
                                                detail_file_number,
                                                actual_day)                
                
                detail_number_2 += 1
                    
                if item == 0:
                
                    if html_switch == "tracks":
                        html_cover = ("""&nbsp;&nbsp;<a href = "track_detail_""" + detail_file_number + 
                                      """.html"><img src="covers/""" + cover_download.main(item_name) + 
                                      """.jpg" width="288" height="162"></a>
         <ol>
         """)
                    elif html_switch == "artists":
                        html_cover = ("""&nbsp;&nbsp;<a href = "artist_detail_""" + detail_file_number + 
                                      """.html"><img src="covers/""" + cover_download.main(item_name) + 
                                      """.jpg" width="288" height="162"></a>
         <ol>
         """)
         
                    file.write(html_cover)
                    file.write(html_list_bold)    
                else:
                    file.write(html_list)            
                
                
                print("█", end = "", flush=True) #monitor
                
            detail_number_1 += 1
            paragraph_count += 1
            
            print("")
            
            if paragraph_count == 3: 
                html_break1 = ("""     </ol>
      </div>
    </div>
    <div class="w3-row-padding">
    """)
                file.write(html_break1)
            else:
                html_break2 =("""     </ol>
      </div>
    """)
                file.write(html_break2)
                
                
            
        html_end = ("""</div>
    <div class="w3-container w3-red">
      <br>
    </div>
    </body>
    </html>""") 
        file.write(html_end)

        file.close()
        
    except sqlite3.Error as error:
        logger.error("Failed:%s", error)
    finally:
        if connection:
            connection.close()
            logger.info("files %s, %s and %s generated", landscape_data[1], landscape_data[2], landscape_data[3] )

main("artists")
main("tracks")

