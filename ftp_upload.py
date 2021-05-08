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

files = ["artists.html", "djs.html", "index.html"]

myFTP = ftplib.FTP("ftp.muteme.cz", "muteme", "kjaEukz7LO")
myFTP.cwd("weloveradio1/")
os.chdir('html/')

for file in files:
    upload = open(file, "rb")
    myFTP.storbinary("STOR %s" % file, upload)
    upload.close()


logger.info("all html files uploaded to ftp")