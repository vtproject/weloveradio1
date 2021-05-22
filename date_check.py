import sqlite3
import datetime
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
cursor = connection.cursor()
cursor.execute("""SELECT * FROM playlist ORDER BY id DESC LIMIT 1""")
record = cursor.fetchone()

date_today = datetime.date.today()
last_retrieve_date = datetime.date(record[12], record[11], record[10])
days_diff = date_today - last_retrieve_date
days_diff = days_diff.days


   
