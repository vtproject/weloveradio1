from bs4 import BeautifulSoup
import requests
import re

url = "https://www.youtube.com/results?search_query=WARPAINT+-+Lilys"
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})
req = requests.get(url,  headers=HEADERS, cookies={'CONSENT': 'YES+cb.20210530-19-p0.en+FX+961'} )
soup = BeautifulSoup(req.content, 'html.parser') 

text = str(soup)

texts = text.split("https://i.ytimg.com/vi/")
for x in range(0,100):
    if re.search('","width":360,"height":202}', texts[x]):
        url_part = texts[x].split('","width":360,"height":202}')
        web_image = "https://i.ytimg.com/vi/" + url_part[0]
        save_image = "pic.jpg"

        print(web_image, " > ", save_image)
          
        response = requests.get(web_image)
        file = open(save_image, "wb")
        file.write(response.content)
        file.close()
        input()
print("new allo")
 


