
import pandas as pd
import math
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine #sqeuclidean
import numpy as np
import time
import logging


def distance(row):
    result = cosine(csr_matrix.toarray(bow_matrix[pos]), csr_matrix.toarray(bow_matrix[row]))
    result = 1 - result
    return(result)

def match_titles(titles):
    intsec = len(np.intersect1d(titles.split(","), base_titles))
    return(intsec)

def match_two(clartist):
    clartist_list = clartist.split()
    base_clartist_list = base_clartist.split()
    if  base_clartist_list[0] == clartist_list[0] and base_clartist_list[1] == clartist_list[1]:
        result = True
    else:
        result = False
    return(result)

def match_one(clartist):
    clartist_list = clartist.split()
    base_clartist_list = base_clartist.split()
    if base_clartist_list[1] == "-" or clartist_list[1] == "-":
        if base_clartist_list[0] == clartist_list[0]:
            result = True
        else:
            result = False
    else:
        result = False
    return(result)


def match_first(row):
    result = cosine(csr_matrix.toarray(bow_matrix_second[pos]), csr_matrix.toarray(bow_matrix_second[row]))
    return(result)

def match_second(row):
    result = cosine(csr_matrix.toarray(bow_matrix_second[pos]), csr_matrix.toarray(bow_matrix_second[row]))
    return(result)      

def match_artists(clartist, jnartist, titles, calcartist, row):
    if calcartist == "-":
        if clartist == base_clartist:
            logger.info(jnartist)
            return(artist_name)
        elif match_two(clartist):
            logger.info(jnartist)
            return(artist_name)
        elif match_titles(titles) > 0:
            if match_one(clartist):
                logger.info(jnartist)
                return(artist_name)
            elif df.iloc[row].to_list()[5] != "-":
                if base_first == df.iloc[row].to_list()[4] and base_second != df.iloc[row].to_list()[5]:
                    if match_second(row) > 0.7:
                        logger.info(jnartist)
                        return(artist_name)
                    else:
                        return("-")
                elif base_first != df.iloc[row].to_list()[4] and base_second == df.iloc[row].to_list()[5]:
                    if match_first(row) > 0.7:
                        logger.info(jnartist)
                        return(artist_name) 
                    else:
                        return("-")
                else:
                    return("-")    
            elif distance(row) > 0.7:
                logger.info(jnartist)
                return(artist_name)
            else:
                return("-")
        else:
            return("-")    
    else:
        return(calcartist)

#logging
if __name__ == "__main__":
    logger = logging.getLogger("run")
else:
    logger = logging.getLogger(__name__)
    
logger.setLevel(logging.INFO)

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
    landscape_data = ["weloveradio1db_P.sqlite"]
elif landscape_switch == "TEST":
    landscape_data = ["weloveradio1db_T.sqlite"]
else:
    landscape_data = ["weloveradio1db_D.sqlite"]

def main(pos_list):
    
    global base_clartist, base_jnartist, base_first, base_second, base_titles, df
    global bow_matrix, bow_matrix_first, bow_matrix_second, pos, artist_name    
        
    con = sqlite3.connect(landscape_data[0])
    cursor = con.cursor()

    df = pd.read_sql_query("SELECT * from artists", con)

    bow_transformer = CountVectorizer(analyzer="char", lowercase=False, ngram_range=(1, 3)).fit(df["jnartist"])
    bow_matrix = bow_transformer.transform(df["jnartist"])
    bow_matrix_first = bow_transformer.transform(df["first_word"])
    bow_matrix_second = bow_transformer.transform(df["second_word"])

    time_global = time.time()
    for row in pos_list:
        pos = row - 1
        if df.iloc[pos].to_list()[6] == "-":
            time_loop = time.time()
            base_clartist = df.iloc[pos].to_list()[1]
            base_jnartist = df.iloc[pos].to_list()[3]
            base_first = df.iloc[pos].to_list()[4]
            base_second = df.iloc[pos].to_list()[5]
            base_titles = df.iloc[pos].to_list()[2].split(",")

            logger.info("---")
            artist_name = base_jnartist

            df["calcartist"] = df.apply(lambda x: match_artists(x.clartist, x.jnartist, x.titles, x.calcartist, x.name), axis=1)
            print(round(time.time()-time_loop, 1), " sec per artist")
            print(round((time.time()-time_global)/60, 1), " minutes running")
        

    cursor.execute("DROP TABLE artists")

    df.to_sql(name="artists", con=con, index=False)
main([1008, 1009, 1010]) 