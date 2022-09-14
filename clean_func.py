import pandas as pd
import numpy as np
import nltk 
import string
import re

from exclude_words import stopwords_indonesia, emoticons
 
#import sastrawi
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

#tokenize
from nltk.tokenize import TweetTokenizer

def load_data():
    data = pd.read_csv('data_test.csv', encoding = "ISO-8859-1")#ubah nama file sesuai dengan nama file
    return data

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
    return input_txt

def remove(tweet):
    # remove stock market tickers like $GE
    tweet = re.sub(r'\$\w*', '', tweet)
    # remove old style retweet text "RT"
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    # remove hyperlinks
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    # remove hashtags
    # only removing the hash # sign from the word
    tweet = re.sub(r'#', '', tweet)
    #remove coma
    tweet = re.sub(r',','',tweet)
    #remove angka
    tweet = re.sub('[0-9]+', '', tweet)
    # remove character 'x'
    tweet = re.sub(r'\b[xX]\w+','',tweet)
    tweet = re.sub(r'\b[xX]','',tweet)
    
    return tweet

def clean_tweets(tweet):
    # remove stock market tickers like $GE
    tweet = re.sub(r'\$\w*', '', tweet)
 
    # remove old style retweet text "RT"
    tweet = re.sub(r'^RT[\s]+', '', tweet)
 
    # remove hyperlinks
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    
    # remove hashtags
    # only removing the hash # sign from the word
    tweet = re.sub(r'#', '', tweet)
    
    #remove coma
    tweet = re.sub(r',','',tweet)
    
    #remove angka
    tweet = re.sub('[0-9]+', '', tweet)

    # remove character 'x'
    tweet = re.sub(r'\b[xX]\w+','',tweet)
    tweet = re.sub(r'\b[xX]','',tweet)
 
    # tokenize tweets
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    tweet_tokens = tokenizer.tokenize(tweet)
 
    tweets_clean = []
    for word in tweet_tokens:
        if (word not in stopwords_indonesia and # remove stopwords
              word not in emoticons and # remove emoticons
                word not in string.punctuation) and word != 'user': # remove punctuation
            #tweets_clean.append(word)
            stem_word = stemmer.stem(word) # stemming word
            tweets_clean.append(stem_word)
    return tweets_clean

def remove_punct(text):
    text  = " ".join([char for char in text if char not in string.punctuation])
    return text

def remove_punct_regex(text):
    remove = re.sub(r'[^\w\s]', '', text)
    return remove

def remove_punct_regex_csv(text):
    pass
    

def cleaned_and_stemmed(path, filename):
    # Store data to variable, and get only the first column
    tweet_df = pd.read_csv(f'{path}', encoding = "ISO-8859-1")
    df = pd.DataFrame(tweet_df.iloc[:, 0])

    # Function to remove username (starts with '@')
    df['remove_user'] = np.vectorize(remove_pattern)(df, "@[\w]*")

    # Function to remove numbers, symbols, etc.)
    df['remove_http'] = df['remove_user'].apply(lambda x: remove(x))
    df.sort_values("remove_http", inplace = True)
    df.drop_duplicates(subset ="remove_http", keep = 'first', inplace = True)

    # Remove links, save to new column
    df['tweet_clean'] = df['remove_http'].apply(lambda x: clean_tweets(x))

    # Remove punctuations, save to new column
    df['Tweet_processed'] = df['tweet_clean'].apply(lambda x: remove_punct(x))

    # Remove duplicates data
    # df.drop_duplicates(keep = 'first', inplace = True)
    df = df.drop(columns=['remove_user', 'remove_http'])
    df.loc[df.astype(str).drop_duplicates().index]

    df.to_csv(f'downloads/{filename}',encoding='utf8', index=False)
    
    