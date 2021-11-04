import ftplib
import os
import logging

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

# TODO: ukazatel průběhu

#landscape
landscape_file = open("landscape.switch", "r")
landscape_switch = landscape_file.read()
landscape_file.close()
if landscape_switch == "PROD":
    landscape_data = ["weloveradio1/", "html_P/"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1_T/", "html_T/"]
else:
    landscape_data = ["weloveradio1_D/", "html_D/"]

logger.info("starting upload to ftp.muteme.cz/%s",landscape_data[0])

from_file = open("file.txt", "r")
files = ["artists.html", "djs.html", "index.html"]
myFTP = ftplib.FTP("ftp.muteme.cz", "muteme", from_file.read())

myFTP.cwd(landscape_data[0])
os.chdir(landscape_data[1])
print("_________")
for file in files:
    upload = open(file, "rb")
    myFTP.storbinary("STOR %s" % file, upload)
    upload.close()
    print("█", end = "", flush=True) #monitor 


for detail_number_1 in range(1, 7):
    for detail_number_2 in range (1, 21):
        detail_name = str(detail_number_1).zfill(2) + "_" + str(detail_number_2).zfill(2)
        
        file = "track_detail_" + detail_name + ".html"
        upload = open(file, "rb")
        myFTP.storbinary("STOR %s" % file, upload)
        upload.close()
        
        file = "artist_detail_" + detail_name + ".html"
        upload = open(file, "rb") 
        myFTP.storbinary("STOR %s" % file, upload)
        upload.close()
        
    print("█", end = "", flush=True) #monitor    
    
print("\n")

from_file.close()
logger.info("all html files uploaded to ftp.muteme.cz/%s",landscape_data[0])