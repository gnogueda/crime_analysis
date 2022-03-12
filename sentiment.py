nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def sentiment_analysis(df):
    '''Calculate neutral, negative and positive sentiment scores 
        and label tweet with highest sentiment

        Inputs: 
            df (DataFrame): df with tweets

        Output: adds sentiment to df
    ''' 
    sid = SentimentIntensityAnalyzer()
    df['sentiment'] = np.nan
    for idx, tweet in enumerate(df['tweet']):
        sentiment_dict = sid.polarity_scores(tweet)
        sentiment_names = ('Negative', 'Positive', 'Neutral')
        sentiment_tup = (sentiment_dict['neg'], sentiment_dict['pos'], sentiment_dict['neu'])
        if np.any(sentiment_tup) > 0.0: # if all values are 0, leave label as nan 
            index = sentiment_tup.index(max(sentiment_tup))
            df['sentiment'][idx] = sentiment_names[index]   