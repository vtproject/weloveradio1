import logging
import date_check
import datetime
import random
import time

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

logger.info("starting job for %s", landscape_switch)
date_today = datetime.date.today()


import date_check
import data_download #no run, waiting for function main()

if date_check.days_diff == 1:
    logger.info("all available data up to %s downloaded already, data_download NOT STARTED", date_check.last_retrieve_date)
elif date_check.days_diff < 1:    
    logger.error("db date mismatch")
else:    
    logger.info("NEW data available, last download was %s", date_today - datetime.timedelta(date_check.days_diff))
    import db_backup
    logger.info("starting download data from %s to %s", date_today - datetime.timedelta(date_check.days_diff-1), date_today - datetime.timedelta(1))

    for day in range(date_check.days_diff-1, 0, -1):
        calculated_execute_date = date_today - datetime.timedelta(day)
        random_wait = random.randrange(2, 6, 1)
        logger.info("waiting for %s seconds to start download", str(random_wait))
        time.sleep(random_wait)        
        data_download.main(calculated_execute_date)



    # print("\n data OK? > Enter")
    # input()

    import html_generator

    # print("\n html OK? > Enter")
    # input()

    import ftp_upload

logger.info("job done \n-----------------------------------------------------------------------")