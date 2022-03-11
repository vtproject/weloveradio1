import pandas as pd
import sqlite3
from unidecode import unidecode
import re
from tqdm import tqdm
tqdm.pandas()

con = sqlite3.connect("weloveradio1db_D.sqlite")
df = pd.read_sql_query("SELECT * from playlist", con)
df = df.drop(["id", "raw_tracklist_no", "raw_tracklist_item_no", "raw_tracklist_dj", "clean_status", "clean_tracklist_dj", "raw_artist", "raw_title", "day", "month", "year", "days_from", "clean_dj_status"], axis=1)


def delminus(artist):
    artist = artist.replace("-"," ")
    artist = artist.split()
    artist = " ".join(artist)
    return(artist)    

df["clean_title"] = df["clean_title"].progress_apply(delminus)

artists_df = df['clean_artist'].value_counts().rename_axis('artists').reset_index(name='counts')
artists_df = artists_df.drop([0], axis=0)
artists_df = artists_df.drop(["counts"], axis=1)

def add_titles(artist):
    return([tup[1] for tup in df[df['clean_artist'] == artist].value_counts().index.tolist()])


artists_df["titles"] = artists_df["artists"].progress_apply(add_titles)

artists_df = artists_df.applymap(str)

artists_df.to_sql(name="artists", con=con)
con.close()


