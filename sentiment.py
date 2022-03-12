nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

# Calculate neutral, negative and positive sentiment scores and label tweet with highest sentiment 
all_chi['sentiment'] = np.nan
for idx, tweet in enumerate(all_chi['tweet']):
    sentiment_dict = sid.polarity_scores(tweet)
    sentiment_names = ('Negative', 'Positive', 'Neutral')
    sentiment_tup = (sentiment_dict['neg'], sentiment_dict['pos'], sentiment_dict['neu'])
    if np.any(sentiment_tup) > 0.0: # if all values are 0, leave label as nan 
        index = sentiment_tup.index(max(sentiment_tup))
        all_chi['sentiment'][idx] = sentiment_names[index]   