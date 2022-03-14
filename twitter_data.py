'''
This file:
    -Scrape tweets

'''

from calendar import month
import twint
import datetime as dt 
import os 
import pandas as pd
import nest_asyncio
import glob
import shutil
import time
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

nest_asyncio.apply() # for working in jupyter notebooks

cities = ["austin"]
#cities = ["new york city", "los angeles", "chicago", "houston", "phoenix",
#"san antonio", "philadelphia", "san diego", "dallas", "austin"]
save_dir = './'
year = 2019
monthhh = 1  # lo normal es 1, se refiere al mes en el que empieza
indices = [1] # lo normal es [0, 1]
#cities = ["new york city", "los angeles", "chicago", "houston", "phoenix",
#"san antonio", "philadelphia", "san diego", "dallas", "austin"]

viol_voc_1 = '''violence violent crime shooting gun murder
assault rape harassment terrorist terrorist
racist robber arrest supremacist sexist
attack trafficking homophobia misogyny injured
weapon narco pedophile abuse victim
danger brutal assassin attack
protest extremist harm rage threat
anger retaliate'''

viol_voc_2 = '''bloody dead deadly death assassinate
ammunition fatal  bullet assault aggressor
dispute brutality ambush hijack hijacker
rape rapist raped victim punch
punched kick stab
weapon knife wound hurt wounded
offense kidnap kidnapped kidnapping abuse
aggressive force suicide bully riot'''

# hate terrified terrifying hit die scary scared fear force blood

viol_voc_3 = '''weapon knife wound hurt wounded
offense kidnap kidnapped kidnapping abuse
aggressive force suicide bully riot
protest extremist harm rage threat
anger retaliate'''

viol_voc = [viol_voc_1, viol_voc_2]
#viol_voc = [viol_voc_1, viol_voc_2]

racism = ['nigger', 'blacky', 'uppity', 'racist', 'racism', 'race', 'racist', 'racism', 'race']
sexism = ['bitch', 'cunt', 'bimbo', 'feminazi']
homophobia = ['fag', 'faggot', 'homo'] # another could be like drugs

def go():
    pass

######################## Tweets scraping section ########################
'''
search_term = 'shooting OR killed OR kill OR shot OR gun OR rifle OR pistol OR murder OR murdered 
OR murderers' OR violence OR violent OR attack OR mug OR mugged OR mugging OR assault OR assaulted 
OR assaulting OR criminal OR criminals OR harass OR harassment OR sexual OR rape OR rapist OR raped 
OR raping OR hit OR punch OR punched OR kick OR stab OR weapon OR knife OR wound OR hurt OR injured 
OR wounded OR offense'  
'''

'''
gang band danger dangerous kidnap kidnapped kidnapping robber robbery steal stole stolen hijacking victim
victims trafficking bomb police fbi death dead died die
'''

'''
start_date = dt.datetime(2021, 2, 1)
end_date = dt.datetime(2021, 2, 3)
save_dir = './'
city = ["new york city"]
td.twint_search_loop(search_term, start_date, end_date, save_dir, city)
path = save_dir + "tweets_downloads2"
path
shutil.rmtree(path)
'''

def twint_search(search_term, since, until, save_path, city):
    c = twint.Config()
    c.Search = search_term
    c.Lang = "en"
    c.Near = city #c.New = city
    c.Limit = 2000000 #10000
    c.Pandas = True
    #print(since)
    #print(since.strftime('%Y-%m-%d %H:%M:%S'))
    print(since.strftime('%Y-%m-%d'))
    print(until.strftime('%Y-%m-%d'))
    c.Since = since.strftime('%Y-%m-%d %H:%M:%S') #"2021-02-01"
    c.Until = until.strftime('%Y-%m-%d %H:%M:%S') #"2021-02-03"
    c.Hide_output = True
    c.Popular_tweets = True
    c.Filter_retweets = True
    #c.Min_likes = 100
    #c.Min_wait_time = 120
    #c.Min_retweets = 1
    c.Store_csv = True
    c.Output = save_path
    #c.Geo = True
    twint.run.Search(c)
    #time.sleep(1)
    
def twint_search_loop(search_term, start_date, end_date, save_dir, city, ind_voc):
    # This is the part that keeps it looping even when it errors
    try:
        os.makedirs(os.path.join(os.getcwd(),save_dir,"tweets_downloads2"))
        print(f'Successfully created the directory {os.path.join(os.getcwd(),save_dir,search_term)}')
    except FileExistsError:
        print(f'Directory {os.path.join(os.getcwd(),save_dir,"tweets_downloads2")} already exists')
    
    date_range = pd.date_range(start_date, end_date)
    
    for single_date in date_range:
        since = single_date
        until = single_date + dt.timedelta(days = 2)
        save_path = os.path.join(save_dir, "tweets_downloads2", f'{single_date:%Y%m%d}{city}{ind_voc}.csv')
        if not os.path.exists(save_path):
        #print(save_path)
            print(f"Searching for tweets containing '{search_term}' from {single_date:%Y-%m-%d} and saving into {save_path}")
            twint_search(search_term, since, until, save_path, city)

def vocabulary_to_search(vocabulary):
    # Let's keep it in 45 words. We can loop every vocabulary
    #potential_crime_string = '''shooting killed kill shot gun rifle pistol murder murdered murderers violence violent attack mug mugged mugging assault assaulted assaulting criminal criminals harass harassment sexual rape rapist raped
    #raping hit punch punched kick stab weapon knife wound hurt injured wounded offense'''
    #''' felony misdemeanor law abuse force battered'''
    #potential_crime_string = '''gang band danger dangerous kidnap kidnapped kidnapping robber robbery steal stole stolen hijacking victim
    #victims trafficking bomb police fbi death dead died die
    #'''

    voc_split = vocabulary.split()
    #print(len(pcs_split))
    voc_split_or = " OR ".join(voc_split)
    return voc_split_or

# td.tweets_scraping(td.viol_voc)
def tweets_scraping(vocabulary):
    #start_date = dt.datetime(2015, 1, 1) # 2021-02-01 # This is feb 1
    start_date = dt.datetime(year, monthhh, 1)
    end_date = dt.datetime(year, 12, 31) # This is feb 3
    save_dir = './'
    for ind_voc, voc in enumerate(vocabulary):
        search_term = vocabulary_to_search(voc)
        # Loop through cities 
        #cities = ["chicago", "new york city"]
        for city in cities:
            if ind_voc in indices: ##### temporal
                twint_search_loop(search_term, start_date, end_date, save_dir, city, ind_voc)

