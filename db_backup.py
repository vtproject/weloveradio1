import shutil
import os
import datetime
import logging

def date_out(datum):
    date_out_f = str(datum)
    date_out_f = datetime.datetime.strptime(date_out_f, '%Y-%m-%d %H:%M:%S.%f')
    date_out_f = date_out_f.strftime('%Y%m%d_%H%M%S_%f')
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
    landscape_data = ["db_backup_P/", "weloveradio1db_P.sqlite", 6] #delete backup threshold
elif landscape_switch == "TEST":
    landscape_data = ["db_backup_T/", "weloveradio1db_T.sqlite", 2]
else:
    landscape_data = ["db_backup_D/", "weloveradio1db_D.sqlite", 2]    
    
destination = landscape_data[0] + date_out(datetime.datetime.now())
source = landscape_data[1]
shutil.copyfile(source, destination)
logger.info("created: %s > %s", source, destination) 

files = os.listdir(landscape_data[0])
if len(files) == landscape_data[2]: #delete backup threshold
    del_file = landscape_data[0] + min(files) 
    os.remove(del_file)
    logger.info("deleted: %s", del_file)