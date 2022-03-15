
# Average Sentiment
import pandas as pd
import os

df = pd.read_csv("tweets_output2021.csv")
# agg.aggregator(df)
def aggregator(df):   
    grouped_df = df.groupby(["near", "Category", "sentiment"])#['jaccard sim score']
    results = grouped_df.mean()
    final = results[['Score_cat']]
    #grouped_df = abbr_frame.groupby(["near", "date"])['sentiment recoded']
    #results['count sentiment'] = grouped_df.mean()
    #final.rename({'jaccard sim score': 'mean jaccard sim score'}, axis=1, inplace=True)
    final.to_csv(os.path.join('./', f'results2021.csv'))