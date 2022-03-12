'''
This file performs:
    -Scrape tweets
    -Text cleaning
    -Cluster in categories of interest
    -Sentiment analysis

'''

import twint
import datetime as dt 
import os 
import pandas as pd
import nest_asyncio
import glob
import shutil
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
nest_asyncio.apply() # for working in jupyter notebooks 

def go():
    pass

######################## Tweets scraping section ########################
def twint_search(search_term, since, until, save_path, city):
    c = twint.Config()
    c.Search = search_term
    c.Lang = "en"
    c.Near = city #c.New = city
    c.Limit = 10000
    c.Pandas = True
    #print(since)
    #print(since.strftime('%Y-%m-%d %H:%M:%S'))
    print(since.strftime('%Y-%m-%d'))
    print(until.strftime('%Y-%m-%d'))
    c.Since = since.strftime('%Y-%m-%d %H:%M:%S') #"2021-02-01"
    c.Until = until.strftime('%Y-%m-%d %H:%M:%S') #"2021-02-03"
    c.Hide_output = True
    c.Store_csv = True
    c.Output = save_path
    twint.run.Search(c)
    
def twint_search_loop(search_term, start_date, end_date, save_dir, city):
    # This is the part that keeps it looping even when it errors
    try:
        os.makedirs(os.path.join(os.getcwd(),save_dir,"tweets_downloads"))
        print(f'Successfully created the directory {os.path.join(os.getcwd(),save_dir,search_term)}')
    except FileExistsError:
        print(f'Directory {os.path.join(os.getcwd(),save_dir,"tweets_downloads")} already exists')
    
    date_range = pd.date_range(start_date, end_date)
    
    for single_date in date_range:
        since = single_date
        until = single_date + dt.timedelta(days=2)
        save_path = os.path.join(save_dir, "tweets_downloads", f'{single_date:%Y%m%d}{city}.csv')
        print(save_path)
        print(f"Searching for tweets containing '{search_term}' from {single_date:%Y-%m-%d} and saving into {save_path}")
        twint_search(search_term, since, until, save_path, city)

def vocabulary_to_search():
    # Let's keep it in 45 words. We can loop every vocabulary
    potential_crime_string = '''shooting killed kill shot gun rifle pistol murder murdered murderers violence violent attack mug mugged mugging assault assaulted assaulting criminal criminals harass harassment sexual rape rapist raped
    raping hit punch punched kick stab weapon knife wound hurt injured wounded offense'''
    ''' felony misdemeanor law abuse force''' # battered'''
    #potential_crime_string = '''gang band danger dangerous kidnap kidnapped kidnapping robber robbery steal stole stolen hijacking victim
    #victims trafficking bomb police fbi death dead died die
    #'''
    pcs_split = potential_crime_string.split()
    #print(len(pcs_split))
    pcs_split_or = " OR ".join(pcs_split)
    return pcs_split_or

def tweets_scraping():
    # Define parameters
    search_term = vocabulary_to_search()
    start_date = dt.datetime(2020, 2, 1) # 2021-02-01 # This is feb 1
    end_date = dt.datetime(2021, 2, 3) # This is feb 3
    #save_dir = '../Desktop/results/'
    save_dir = './'
    # Loop through cities 
    cities = ["chicago", "new york city"]
    for city in cities: 
        twint_search_loop(search_term, start_date, end_date, save_dir, city)

def tweets_df():
    path = save_dir + "tweets_downloads"# use your path
    all_files = glob.glob(path + "/*.csv")

    files_data = []

    for file in all_files:
        df = pd.read_csv(file, index_col=None, header=0)
        files_data.append(df)

    dframe = pd.concat(files_data, axis=0, ignore_index=True)
    # Delete the folder and its files.
    #shutil.rmtree(path) ####### This will go to the final version
    return dframe

######################## Cleaning section ########################

######################## Clustering section ########################
social = '''sociable, gregarious societal friendly society socialization political  sociality 
                        interpersonal  ethnic socially party welfare public community socialist societies development
                            network humans socialism collective personal corporation social constructivism
                        relations volition citizenship brute   attitude rights socio 
                        socioeconomic ethics civic communal marital  sociale socialized communities     
                         policy   unions        
                        institutions values     governmental   organizations jamboree 
                         festivity    fairness  support  care  
                         sides   activism     unsocial psychosocial 
                        socializing psychological distributional  demographic  participation reunion 
                        partygoer partyism festive power network gala housewarming celebration counterparty   social-war
                        particularist interactional ideational asocial'''

health = '''disease obesity world health organization medicine nutrition well-being exercise welfare wellness health care public health 
                     nursing stress safety hygiene research social healthy condition aids epidemiology healthiness wellbeing
                     care illness medical dieteducation infectious disease environmental healthcare physical fitness hospitals 
                     health care provider doctors healthy community design insurance sanitation human body patient mental health
                      medicare agriculture health science fitnesshealth policy  weight loss physical therapy psychology pharmacy
                     metabolic organism human lifestyle status unhealthy upbeat vaccination sleep condom alcohol smoking water family
                     eudaimonia eudaemonia air house prevention genetics public families poor needs treatment communicable disease 
                     study protection malaria development food priority management healthful mental provide department administration
                     programs help assistance funding environment improving emergency need program affected schools private mental illness 
                     treat diseases preparedness perinatal fertility sickness veterinary sanitary pharmacists behavioral midwives
                     gerontology infertility hospitalization midwifery cholesterol childcare pediatrician pediatrics medicaid asthma 
                     pensions sicknesses push-up physical education body-mass-index eat well gymnastic apparatus tune up good morning 
                     bathing low blood-pressure heart attack health club ride-bike you feel good eczema urticaria dermatitis sunburn overwork 
                     manufacturing medical sociology need exercise run'''




def get_vectors(*strs):
    '''Vectorizing the sets of words, then standardizing them. TFIDF will be used in order to take care of the least 
    frequent words. Standardizing is cause TFIDF favors long sentences and there'll be inconsistencies between the length 
    of the tweets and the length of set of words.'''
    text = [t for t in strs]
    vectorizer = TfidfVectorizer(text)
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()

'''Jaccard similarity is good for cases where duplication does not matter, 
cosine similarity is good for cases where duplication matters while analyzing text similarity. For two product descriptions, 
it will be better to use Jaccard similarity as repetition of a word does not reduce their similarity.'''

def jaccard_similarity(query, document):
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return len(intersection)/len(union)

def get_scores(group,tweets):
    scores = []
    for tweet in tweets:
        s = jaccard_similarity(group, tweet)
        scores.append(s)
    return scores

def tweets_clustering():
    socialvector = get_vectors(social)
    healthvector = get_vectors(health)

    df = tweets_df()
    ## Vectorizing the tweets
    tv=TfidfVectorizer()
    # tweets_bowl = tweets_bowl.tweets.apply(get_vectors)
    # tweets_bowl.head()
    tfidf_tweets =tv.fit_transform(df.tweet)

    scores1 = get_scores(social, df.tweet.to_list())
    scores2 = get_scores(health, df.tweet.to_list())
    return (scores1, scores2)

######################## Sentiment Analysis section ########################