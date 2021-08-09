import sqlite3
import datetime
import urllib.parse
import re
import logging
import html_detail_generator
import cover_download

def date_out(datum):
    date_out_f = str(datum)
    date_out_f = datetime.datetime.strptime(date_out_f, '%Y-%m-%d')
    date_out_f = date_out_f.strftime('%#d.%#m.%Y')
    return date_out_f

def retrieve_chart_tracks(from_day, to_day, days_back):
    cursor = connection.cursor()
    from_day = from_day - days_back
    to_day = to_day - days_back    
   
    cursor.execute("""
    SELECT
        clean_artist, clean_title, COUNT(clean_title)
    FROM
        playlist
    WHERE clean_status = 1 AND days_from BETWEEN """ + str(from_day) + """ AND """ + str(to_day) + """
    GROUP BY
        clean_artist, clean_title
    ORDER BY
        COUNT(clean_title) DESC,
        clean_artist ASC;
    """)
    record = cursor.fetchall()
    chart_list = []
          
    for chart_row in range(0, 20):
        chart_item_artisttitle = record[chart_row]
        if chart_item_artisttitle[2] < 2:
            chart_item_full = ["-",""]
        else:
            artisttitle = chart_item_artisttitle[0] + " - " + chart_item_artisttitle[1]
            chart_item_full = [artisttitle, chart_item_artisttitle[2], chart_item_artisttitle[0], chart_item_artisttitle[1]]
        chart_list.append(chart_item_full)
        cursor.close()
    return(chart_list)

def retrieve_chart_artists(from_day, to_day, days_back):
    cursor = connection.cursor()
    
    from_day = from_day - days_back
    to_day = to_day - days_back    
   
    cursor.execute("""
    SELECT clean_artist, count(clean_artist)
    FROM   (SELECT
        clean_artist
    FROM
        playlist
    WHERE clean_status = 1 AND days_from BETWEEN """ + str(from_day) + """ AND """ + str(to_day) + """
    GROUP BY
        clean_artist, raw_tracklist_no)
    GROUP BY 
	clean_artist
    ORDER BY
	COUNT(clean_artist) DESC,
	clean_artist ASC;
    """)
    record = cursor.fetchall()
    chart_list_tracks = []
    for chart_row in range(0, 20):
        chart_item_full = record[chart_row]
        if chart_item_full[1] < 2:
            chart_item_full = ["-",""]
        chart_list_tracks.append(chart_item_full)
        cursor.close()
    return(chart_list_tracks)

def retrieve_djs(from_day, to_day):
    global djs_lst, dj_tracks_lst
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        clean_tracklist_dj, COUNT(clean_tracklist_dj)
    FROM
        playlist
    WHERE clean_dj_status = 1 AND days_from BETWEEN """ + str(from_day) + """ AND """ + str(to_day) + """
    GROUP BY
        clean_tracklist_dj
    ORDER BY
        COUNT(clean_tracklist_dj) DESC,
        clean_tracklist_dj ASC;
    """)
    record = cursor.fetchall()
    djs_lst = []
    dj_tracks_lst = []
    for chart_row in range(0, len(record)):
        djs_all = record[chart_row]
        djs_lst.append(djs_all[0])
        dj_tracks_lst.append(str(djs_all[1]))
        cursor.close()

def retrieve_dj_chart(dj, from_day, to_day, days_back):
    cursor = connection.cursor()
    
    from_day = from_day - days_back
    to_day = to_day - days_back      
           
    cursor.execute("""
    SELECT
        clean_artist, clean_title, COUNT(clean_title)
    FROM
        playlist
    WHERE clean_status = 1 AND clean_tracklist_DJ ='""" + dj + """' AND days_from BETWEEN """ + str(from_day) + """ AND """ + str(to_day) + """
    GROUP BY
        clean_artist, clean_title
    ORDER BY
        COUNT(clean_title) DESC,
        clean_artist ASC;
    """)
    record = cursor.fetchall()
    chart_list_tracks = []
    for chart_row in range(0, 20):
        chart_item_artisttitle = record[chart_row]
        if chart_item_artisttitle[2] < 2:
            chart_item_full = ["-",""]
        else:
            artisttitle = chart_item_artisttitle[0] + " - " + chart_item_artisttitle[1]
            chart_item_full = [artisttitle, chart_item_artisttitle[2]]                    
        chart_list_tracks.append(chart_item_full)
        cursor.close()
    return(chart_list_tracks)

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
    landscape_data = ["weloveradio1db_P.sqlite", "html_P/index.html", "html_P/artists.html", "html_P/djs.html"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1db_T.sqlite", "html_T/index.html", "html_T/artists.html", "html_T/djs.html"]
else:
    landscape_data = ["weloveradio1db_D.sqlite", "html_D/index.html", "html_D/artists.html", "html_D/djs.html"]

connection = sqlite3.connect(landscape_data[0])
        
paragraph_count = 0

update_date = datetime.date.today()  # Datum generování datetime.date(2021, 4, 3)  datetime.date.today() 
execute_date = update_date - datetime.timedelta(1) # Datum generování html  

actual_day = execute_date - datetime.date(2012, 9, 29)
actual_day = actual_day.days
days_back = [7, 30, 183, 365, 1825, 3650]
chart_name = ["za minulý týden", "za minulý měsíc", "za minulých 6 měsíců", "za minulý rok", "za minulých 5 let", "za minulých 10 let"]
chart_period = ["v minulém týdnu", "v minulém měsíci", "v minulých 6 měsících", "v minulém roce", "v minulých 5 letech", "v minulých 10 letech"]
try:
    logger.info("starting tracks, details and artists html generator from %s", landscape_data[0]) 
    
    file_tracks = open(landscape_data[1], "w") #delete previous test file 
    file_artists = open(landscape_data[2], "w") 
    file_djs = open(landscape_data[3], "w") 
    file_tracks.close()
    file_artists.close()
    file_djs.close()

    file_tracks = open(landscape_data[1], "a", encoding = "utf-8")
    file_artists = open(landscape_data[2], "a", encoding = "utf-8")
    file_djs = open(landscape_data[3], "a", encoding = "utf-8")
    
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

    html_menu_tracks =("""<div class="w3-container">
  <h4>| nejhranější skladby |&nbsp;<a href = "artists.html"><U>nejhranější&nbsp;skupiny</U></a>&nbsp;|<br>
| <a href = "djs.html"><U>žebříčky podle moderátorů</U></a> |</h4> 
</div>
<div class="w3-row-padding">
""")
    
    html_menu_artists =("""<div class="w3-container">
  <h4>| <a href = "index.html"><U>nejhranější skladby</U></a> |&nbsp;nejhranější&nbsp;skupiny&nbsp;|<br>
| <a href = "djs.html"><U>žebříčky podle moderátorů</U></a> |</h4> 
</div>
<div class="w3-row-padding">
""")

    html_menu_djs = ("""<div class="w3-container">
  <h4>| <a href = "index.html"><U>nejhranější skladby</U></a> |&nbsp;<a href = "artists.html"><U>nejhranější&nbsp;skupiny</U></a>&nbsp;|<br>
| žebříčky podle moderátorů |</h4> 
</div>
<div class="w3-row-padding">
""")
    
    file_tracks.write(html_header)
    file_tracks.write(html_menu_tracks)
    
    file_artists.write(html_header)
    file_artists.write(html_menu_artists)
    
    file_djs.write(html_header)
    file_djs.write(html_menu_djs)
    
    print("      ____________________") #progress bar
        
    detail_number_1 = 1
        
    for chart_no in range(0,6):            
        
        chart_no_monitor = chart_no + 1
        print("%s/6 > " % chart_no_monitor, end = "", flush=True) #monitor
        
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
        file_tracks.write(html_list_dates)
        file_artists.write(html_list_dates)
        
        chart_list_tracks = retrieve_chart_tracks(from_day, to_day, 0)
        chart_list_tracks_last = retrieve_chart_tracks(from_day, to_day, 1)
        
        chart_list_artists = retrieve_chart_artists(from_day, to_day, 0)
        chart_list_artists_last = retrieve_chart_artists(from_day, to_day, 1)        
        detail_number_2 = 1

###########################################################generate index.html
        for item in range(0, 20):
            print("█", end = "", flush=True) #monitor 
            
            if chart_list_tracks[item][0] == "-":
                html_list_tracks = '        <li>-</li>\n' 
            else:
                for track_last in chart_list_tracks_last:
                    arrow = "*&nbsp;"  
                    if chart_list_tracks[item][0] == track_last[0]:                     
                        if chart_list_tracks[item][1] > track_last[1]:
                            arrow = "&uarr;&nbsp;" 
                        elif chart_list_tracks[item][1] < track_last[1]:
                            arrow = "&darr;&nbsp;" 
                        else:
                            arrow = "&nbsp;&nbsp;"
                        break    
                detail_file_number = str(detail_number_1).zfill(2) + "_" + str(detail_number_2).zfill(2)                 
                
                html_list_tracks = '        <li><span style="color:red">' + arrow +  '</span><a href = "track_detail_' + detail_file_number + '.html">' + chart_list_tracks[item][0] + ' <img src="link.png" width="10" height="10"></a> (' + str(chart_list_tracks[item][1]) + ')</li>\n'
                html_list_tracks_bold = '        <li><span style="color:red">' + arrow +  '</span><a href = "track_detail_' + detail_file_number + '.html"><b>' + chart_list_tracks[item][0] + '</b> <img src="link.png" width="10" height="10"></a> (' + str(chart_list_tracks[item][1]) + ')</li>\n'

                html_detail_generator.main(str(chart_list_tracks[item][2]), str(chart_list_tracks[item][3]),detail_file_number,days_back[chart_no],chart_period[chart_no])
                detail_number_2 += 1
                
            if item == 0:
                html_cover = """&nbsp;&nbsp;<a href = "track_detail_""" + detail_file_number + """.html"><img src="covers/""" + cover_download.main(chart_list_tracks[0][0]) + """.jpg" width="288" height="162"></a>
     <ol>
     """
                file_tracks.write(html_cover)
                file_tracks.write(html_list_tracks_bold)    
            else:
                file_tracks.write(html_list_tracks)            
            
###########################################################generate artists.html             

            if chart_list_artists[item][0] == "-":
                html_list_artists = '        <li>-</li>\n' 
            else:
                for artist_last in chart_list_artists_last:
                    arrow = "*&nbsp;"               
                    if chart_list_artists[item][0] == artist_last[0]:
                        if chart_list_artists[item][1] > artist_last[1]:
                            arrow = "&uarr;&nbsp;"
                        elif chart_list_artists[item][1] < artist_last[1]:
                            arrow = "&darr;&nbsp;"
                        else:
                            arrow = "&nbsp;&nbsp;"
                        break    
                html_list_artists = '        <li><span style="color:red">' + arrow +  '</span><a href = "https://www.discogs.com/search/?q=' + urllib.parse.quote_plus(chart_list_artists[item][0]) + '" target="_blank">' + chart_list_artists[item][0] + '</a> (' + str(chart_list_artists[item][1]) + ')</li>\n'
            file_artists.write(html_list_artists)
            
        detail_number_1 += 1
        paragraph_count += 1
        
        print("")
        
        if paragraph_count == 3: 
            html_break1 = ("""     </ol>
  </div>
</div>
<div class="w3-row-padding">
""")
            file_tracks.write(html_break1)
            file_artists.write(html_break1)
        else:
            html_break2 =("""     </ol>
  </div>
""")
            file_tracks.write(html_break2)
            file_artists.write(html_break2)
            
            
        
    html_end = ("""</div>
<div class="w3-container w3-red">
  <br>
</div>
</body>
</html>""") 
    file_tracks.write(html_end)
    file_artists.write(html_end)

    file_tracks.close()
    file_artists.close()
    
###########################################################generate djs.html 
    
    to_day = actual_day
    from_day = 0 # actual_day - 185
    
    chart_out = []
    chart_count_out = []
    paragraph_count = 0
    dj_count = 0
    
    print("")
    logger.info("starting djs generator from %s", landscape_data[0]) 
    print("_________________________________________________________________") #progress bar

    retrieve_djs(from_day, to_day)
    for dj in djs_lst:
       
        chart_list_tracks = retrieve_dj_chart(dj, from_day, to_day, 0)
        chart_list_tracks_last = retrieve_dj_chart(dj, from_day, to_day, 1)
        
        file_djs.write("""  <div class="w3-third">
    <h2> <b>""" + dj + """</b> (""" + str(dj_tracks_lst[dj_count]) +""" skladeb za 10 let) </h2>  
      <ol>
""")
        
        for item in range(0, 20):           
            if chart_list_tracks[item][0] == "-":
                html_list_tracks = '        <li>-</li>\n' 
            else:
                for track_last in chart_list_tracks_last:
                    arrow = "*&nbsp;"  
                    if chart_list_tracks[item][0] == track_last[0]:                     
                        if chart_list_tracks[item][1] > track_last[1]:
                            arrow = "&uarr;&nbsp;" 
                        elif chart_list_tracks[item][1] < track_last[1]:
                            arrow = "&darr;&nbsp;" 
                        else:
                            arrow = "&nbsp;&nbsp;"
                        break    
                html_list_tracks = '        <li><span style="color:red">' + arrow +  '</span><a href = "https://www.youtube.com/results?search_query=' + urllib.parse.quote_plus(chart_list_tracks[item][0]) + '" target="_blank">' + chart_list_tracks[item][0] + '</a> (' + str(chart_list_tracks[item][1]) + ')</li>\n'
            file_djs.write(html_list_tracks)
          
        paragraph_count += 1

        if paragraph_count % 3 == 0:
            file_djs.write(html_break1)
        else:
            file_djs.write(html_break2)
        dj_count = dj_count + 1
        
        print("█", end = "", flush=True) #monitor
     
    print("\n")
    file_djs.write(html_end)
    file_djs.close()
 
except sqlite3.Error as error:
    logger.error("Failed:%s", error)
finally:
    if connection:
        connection.close()
        logger.info("files %s, %s and %s generated", landscape_data[1], landscape_data[2], landscape_data[3] )
        logger.info("db %s closed", landscape_data[0])


