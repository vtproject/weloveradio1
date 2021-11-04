from bs4 import BeautifulSoup
import requests
import re
import datetime
import logging
import urllib.parse
import os.path
import ftplib

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
    landscape_data = ["weloveradio1/covers/", "html_P/covers/"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1_T/covers/", "html_T/covers/"]
else:
    landscape_data = ["weloveradio1_D/covers", "html_D/covers/"]



def main(artisttitle):
    date_today = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d').strftime('%Y%m%d')
    cookie_consent = "YES+cb." + date_today + "-19-p0.en+FX+961"
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(artisttitle)

    HEADERS = ({'User-Agent':     
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
                'Accept-Language': 'en-US, en;q=0.5'})
    
    pic_name = artisttitle.replace(" ","_")
    save_image = pic_name +".jpg" 
    save_image_path = landscape_data[1] + pic_name +".jpg"    
    from_file = open("file.txt", "r")
    
    if os.path.isfile(save_image_path) is False:
        req = requests.get(url,  headers=HEADERS, cookies={'CONSENT': cookie_consent} )
        soup = BeautifulSoup(req.content, 'html.parser') 

        text = str(soup)
        texts = text.split("https://i.ytimg.com/vi/")
        target_part = texts[1].split('","width":360,"height":202}')
        web_image = "https://i.ytimg.com/vi/" + target_part[0]
        
        response = requests.get(web_image)
        file = open(save_image_path, "wb")
        file.write(response.content)
        file.close()
        
        myFTP = ftplib.FTP("ftp.muteme.cz", "muteme", from_file.read())
        myFTP.cwd(landscape_data[0])
        # os.chdir(landscape_data[1])

        upload = open(save_image_path, "rb")
        myFTP.storbinary("STOR %s" % save_image, upload)
        upload.close()
    
    return pic_name