from bs4 import BeautifulSoup
import requests
import re
import datetime

date_today = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d').strftime('%Y%m%d')
cookie_consent = "YES+cb." + date_today + "-19-p0.en+FX+961"
artisttitle = "YVES TUMOR - Jackie"
url = "https://www.youtube.com/results?search_query=YVES+TUMOR+-+Jackie"

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})

req = requests.get(url,  headers=HEADERS, cookies={'CONSENT': cookie_consent} )
soup = BeautifulSoup(req.content, 'html.parser') 

text = str(soup)
texts = text.split("https://i.ytimg.com/vi/")
target_part = texts[1].split('","width":360,"height":202}')

web_image = "https://i.ytimg.com/vi/" + target_part[0]
pic_name = artisttitle.replace(" ","_")
save_image = "html_D/covers/" + pic_name +".jpg"

response = requests.get(web_image)
file = open(save_image, "wb")
file.write(response.content)
file.close()




