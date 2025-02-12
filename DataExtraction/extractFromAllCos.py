
from datetime import datetime
import pandas as pd
from textblob import TextBlob
from langdetect import detect
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *

def load_csv():
    df = pd.read_csv("/Users/darryl/y2s2/is3107/projectgit/IS3107/DataExtraction/stock_tweets.csv")
    df = df[["Date", "Tweet", "Stock Name"]]
    df = df.rename(columns={"Date": "Date", "Tweet" : "Tweet", "Stock Name": "StockName"})
    print("Successfully loaded!")
    return df

def filter_valid_dates(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S%z')
        return True
    except ValueError:
        return False

def clean_data():
    df = load_csv()
    valid_dates_mask = df['Date'].apply(filter_valid_dates)
    df = df[valid_dates_mask]
    print(df["Date"])
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d %H:%M:%S%z")
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["Tweet"] = df["Tweet"].str.replace(r"http\S+", "")
    df["Tweet"] = df["Tweet"].str.replace(r"@\S+", "")
    df["Tweet"] = df["Tweet"].str.replace(r"#\S+", "")
    df["Tweet"] = df["Tweet"].str.strip()
    df.to_csv("allCompanyTweetsCleaned.csv", index=False)
    print("Successfully cleaned!")
    df.dropna()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by='Date', ascending=False)
    df.reset_index(inplace=False)
    df.to_gbq("is3107-project-383009.Dataset.allStockTweetsCleaned", project_id="is3107-project-383009", if_exists='replace')
    print("Successfully loaded into GBQ!")
    return df

def sentiment_score_transform(data):
    # data['Tweet'] = data['Tweet'].astype(str) #Change the tweet data type from object to string
    data.dropna(subset=['Tweet'], inplace=True) #drop rows with na values in Tweet column
    data.reset_index(drop=True, inplace=True) #reset indexes and drop the old index column
    sia = SentimentIntensityAnalyzer()
    data['Sentiments'] = data['Tweet'].apply(lambda Tweet: sia.polarity_scores(Tweet))
    data = pd.concat([data.drop(['Sentiments'], axis=1), data['Sentiments'].apply(pd.Series)], axis=1)
    data.to_gbq("is3107-project-383009.Dataset.allStocksAnalysed", project_id="is3107-project-383009", if_exists='replace')
    # print(data)
    return data


combined = clean_data()
sentiment_score_transform(combined)



