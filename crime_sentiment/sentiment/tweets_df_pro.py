'''
This file:
    -Text cleaning
    -Cluster in categories of interest
    -Sentiment analysis

'''

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
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nest_asyncio.apply() # for working in jupyter notebooks
stopwords = stopwords.words('english')
stopwords = set(stopwords)

save_dir = os.path.abspath(os.path.join(__file__ ,"../..")) + "/data/twitter/sentiment_disaggregated_results/"
save_dir = os.path.abspath(os.path.join(__file__ ,"../..")) + "/data/twitter/sentiment_disaggregated_results/"


# tdp.tweets_processing("tweets_output", "2017") ############# year must be a string
def tweets_processing(input_directory_name, output_filename, year):
    df = tweets_df()
    df = df[df['date'].str.slice(stop=4) == year]
    clean_all_tweets(df)
    tweets_clustering(clust_cat, df)
    sentiment(df)
    df.to_csv(os.path.join('./', f'{output_filename}{year}.csv'))


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
hate = ''' racism nigger blacky uppity sexism bitch cunt bimbo feminazi homophobia fag faggot homo black
racism racist bigotry blm caucusing blackness colonization white whites supremacist blacks poc appropiation
culture genocide diaspora anti semitic zionist jew jews discrimination superiority diversity speech ethnic
ethnicity indigenity indigenous native american english spanish language country tolerance intolerance
dominance intersectionality marginalization beans border foreign minority woman women people oppression
power prejudice race racial identity equity racialization reparations social muslim arabs chinese asian asians
nigga privilege supremacy xenophobia kkk ku klux klan pig abbie abe abie afro african colored karen
ape jemima beaner beaney bluegum bootlip brownie buddhahead indian burr ching ching coconut coon cracker
crow greaser jap jewboy nip oreo rastus sambo latinos latino wetback natzi sheeny snowflake wigger wigga
trash wop zipperhead gay lesbian lgbt queer shemale tranny trans cuntboy chic radical digger bitches slut
cougar hysteria female whore parasites nationalist nationalism patriotism misogyny mannish bitchy hate diva
frigid man-eater prude mumsy neurotic hysteria pregnant abortion rights civil tomboy catfight botchfest
sissy effeminate fear bullying bully bisexual homo homophobic limp-wristed dyke flamer sod sodomite twink
lesbo fairy poof drag pansy antipathy detest abhor disgust disgusting pussy empathy antipathy aversion
hijab camel sand hitler lynch lynching mexican
'''

guns = '''gun guns shot shoot shooting load rifle bullet target aim control regulation law misfire ballistic
firearm firearms act 1968 owners protection private property weapons assault ban second amendment national association
lives march gunowners america automatic semiautomatic caliber brady handgun mass gunman bump stocks binary
trigger pistol pistols shooters school suppressor high capacity reload killer suicide ak ak-47 ar-65 trigger
bullets bulletproof barrel machine-gun laws prohibition permit purchase unlicensed mental illness background
check records dealer registration advocates gunshot massacre columbine discharging unarmed hostage tragedy
slaughter annihilation shooter sniper marksman accident gunner piece rod heater revolver derringer fatal
fatality killed kills death headshot execution execute puller gun-owners license nra sandyhook common sense
roght bear self-defense pulse arms
'''

crimes = '''police ribber kidnap assault mug mugger mugging murder murderer killer violent crime robber
robbery attack rape rapist hurt injur victim justice aggresor hijack hijacker punch hit assasin attack
harm arrest crimes criminal abduction assassination burglar burglary homicide hooliganism theft
looting manslaughter pickpocketing trespassing lynching victim accomplice offender harrasment harras
fbi first degree felony malice aforethought unlawful kill premeditation aggravate permissive strangulation
strangulate poisoning terminatins harm detrimental punishment prison jail deliberation life sexual
pedophile pederast perpetrator abuse violence cash wallet phone laptop computer belongings money guilt
guilty larceny threat wound battery weapon gun shot knife car force intercourse gang invasion consent
ravish violate rob loot bang
'''

addictions = '''drugs alcohol tobacco smoking cigarrette cigar joint snuff addict junk disease drugging rehab
rehabilitation trafficking narco narcotics inject substance marijuana smoker rolling paper roach clip dealer
drinker social drink hallucinate hallucinogen beer cocaine coke crack coca narc hooka hash liquor liqueur pot
weed grass dope pass kilo heroin fentanyl od overdose mescaline nark size popper depressant deviant pusher
tranquilizer peyote therapy amphentanile angel dust tequila scotch whiskey gin vodka rum alcoholic anonymous
party pipe push lsd pills ecstasy tonic clean sniff line mainline cook methamphetamine meth crank steroid
pass bottom out drunkard blackout pot-head stoned dependent dependency cut columbian downer flashback
amphentamine cocktail depressant teetotaler screwdriver roll bong chug prescription prescribe pharmacist
toke symptom hangover paraphernalia bennie hypodermic caffeine habit mushrooms bar snort stimulant glue
relapse abstinence street sniff smack drunkard pill tolerance therapy champagne sober spoon opium opioid
lid bust boost booze intervention rolling abuse treatment brandy illegal crystal acid green gold
herb bash flake snow powder blue tranqs chalk health addiction hospital hospitalize hospitalise clinic
needle vessels na aa 12 steps twelve steps addicted addictive gateway
'''

clust_cat = {'hate' : hate, 'guns' : guns, 'crimes' : crimes, 'addictions' : addictions}

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
    for cat, voc in clust_cat.items():
        #vect = get_vectors(cat)

        ## Vectorizing the tweets
        #tv = TfidfVectorizer() ############### ver si se ocupa o bye
        # tweets_bowl = tweets_bowl.tweets.apply(get_vectors)
        # tweets_bowl.head()
        #tfidf_tweets = tv.fit_transform(df.tweet) ########## ver si se ocupa o bye

        df[cat] = get_scores(voc, df.tweet.to_list())
        df['Score_cat'] = df[['Score_cat', cat]].max(axis = 1)
        df['Category'][df['Score_cat'] == df[cat]] = cat ############
        
#df1 = pd.DataFrame({'name': ['Raphael', 'Donatello'], 'mask': ['2016-12-02', '2014-12-02'],'weapon': [1, 10]})
#df1['Score_cat'] = df1[['mask', 'weapon']].max(axis=1)
#df1['Category'] = None
#df1['Category'][df['Score_cat'] == df['mask']] = "hey"

######################## Sentiment Analysis section ########################

def sentiment(df): 
    sid = SentimentIntensityAnalyzer() # Calculate neutral, negative and positive sentiment scores and label tweet with highest sentiment 
    df['sentiment'] = None #np.nan
    for idx, tweet in enumerate(df['tweet']):
        sentiment_dict = sid.polarity_scores(tweet)
        sentiment_names = ('Negative', 'Positive', 'Neutral')
        sentiment_tup = (sentiment_dict['neg'], sentiment_dict['pos'], sentiment_dict['neu'])
        if np.any(sentiment_tup) > 0.0: # if all values are 0, leave label as nan #########
            index = sentiment_tup.index(max(sentiment_tup))
            #print(index)
            #print(idx)
            df['sentiment'].iloc[[idx]] = sentiment_names[index] ############
            #print(df['sentiment'][idx])
    df['Tweets'] = df['tweet']
    df.drop(['tweet'], axis = 1, inplace = True)
