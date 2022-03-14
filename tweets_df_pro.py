'''
This file:
    -Text cleaning
    -Cluster in categories of interest
    -Sentiment analysis

'''

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')

import numpy as np
import re
import twint
import datetime as dt 
import os 
import pandas as pd
import nest_asyncio
import glob
import shutil
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nest_asyncio.apply() # for working in jupyter notebooks
stopwords = stopwords.words('english')
stopwords = set(stopwords)

def tweets_processing(output_filename):
    df = tweets_df()
    clean_all_tweets(df)
    tweets_clustering(clust_cat, df)
    sentiment(df)
    df.to_csv(os.path.join('./', f'{output_filename}.csv'))


######################## Create a data frame of the Tweets ########################
def tweets_df():
    path = './' + "tweets_downloads2"# use your path
    all_files = glob.glob(path + "/*.csv")

    files_data = []

    for file in all_files:
        df = pd.read_csv(file, index_col=None, header=0)
        files_data.append(df)

    dframe = pd.concat(files_data, axis=0, ignore_index=True)
    dframe = dframe[['id', 'date', 'time', 'near', 'tweet']]
    dframe = dframe.set_index('id')
    dframe = dframe.drop_duplicates() # if it's slow try with subset inside drop_duplicates
    # Delete the folder and its files.
    #shutil.rmtree(path) ####### This will go to the final version

    return dframe

######################## Cleaning section ########################

def clean_all_tweets(frame):
    frame['tweet'] = frame['tweet'].map(lambda x: clean_tweet(x))

def clean_tweet(tweet):
    if type(tweet) == np.float:
        return ""
    temp = tweet.lower()
    temp = re.sub("'", "", temp) # to avoid removing contractions in english
    temp = re.sub("@[A-Za-z0-9_]+","", temp)
    temp = re.sub("#[A-Za-z0-9_]+","", temp)
    temp = re.sub(r'http\S+', '', temp)
    temp = re.sub('[()!?]', ' ', temp)
    temp = re.sub('\[.*?\]',' ', temp)
    temp = re.sub("[^a-z0-9]"," ", temp)
    temp = temp.split()
    temp = [w for w in temp if not w in stopwords]
    temp = " ".join(word for word in temp)
    return temp

######################## Clustering section ########################
hate = ''' racism nigger blacky uppity sexism bitch cunt bimbo feminazi homophobia fag faggot homo
'''

guns = '''gun guns 
'''

crimes = '''disease 
'''

addictions = '''disease 
'''

clust_cat = [hate, guns, crimes, addictions]

#def get_vectors(*strs):
#    '''Vectorizing the sets of words, then standardizing them. TFIDF will be used in order to take care of the least 
#    frequent words. Standardizing is cause TFIDF favors long sentences and there'll be inconsistencies between the length 
#    of the tweets and the length of set of words.'''
#    text = [t for t in strs]
#    vectorizer = TfidfVectorizer(text)
#    vectorizer.fit(text)
#    return vectorizer.transform(text).toarray()

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

def tweets_clustering(clust_cat, df):
    df['Score_cat'] = 0
    df['Category'] = None
    for cat in clust_cat:
        #vect = get_vectors(cat)

        ## Vectorizing the tweets
        #tv = TfidfVectorizer() ############### ver si se ocupa o bye
        # tweets_bowl = tweets_bowl.tweets.apply(get_vectors)
        # tweets_bowl.head()
        #tfidf_tweets = tv.fit_transform(df.tweet) ########## ver si se ocupa o bye

        df[cat] = get_scores(cat, df.tweet.to_list())
        df['Score_cat'] = max(df['Score_cat'], df[cat])
        df['Category'][df['Score_cat'] == df[cat]] = cat
        

######################## Sentiment Analysis section ########################

def sentiment(df): 
    sid = SentimentIntensityAnalyzer() # Calculate neutral, negative and positive sentiment scores and label tweet with highest sentiment 
    df['sentiment'] = np.nan
    for idx, tweet in enumerate(df['tweet']):
        sentiment_dict = sid.polarity_scores(tweet)
        sentiment_names = ('Negative', 'Positive', 'Neutral')
        sentiment_tup = (sentiment_dict['neg'], sentiment_dict['pos'], sentiment_dict['neu'])
        if np.any(sentiment_tup) > 0.0: # if all values are 0, leave label as nan 
            index = sentiment_tup.index(max(sentiment_tup))
            df['sentiment'][idx] = sentiment_names[index] 

