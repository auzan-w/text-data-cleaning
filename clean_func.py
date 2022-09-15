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

def clean_text(tweet):
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
    
    tweet = re.sub(r'[^\w\s]', '', tweet)
    
    return tweet

def clean_and_stem_text(tweet):
    tweet = clean_text(tweet)
 
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
    tweets_clean = ' '.join(tweets_clean)
    return tweets_clean

def clean_csv(path, filename):
    df = pd.read_csv(f'{path}', encoding = "ISO-8859-1")
    df = pd.DataFrame(df.iloc[:, 0])
    
        # Function to remove username (starts with '@')
    df['remove_user'] = np.vectorize(remove_pattern)(df, "@[\w]*")

    # Remove numbers, symbols, links, and duplicates data)
    df['remove_symbols'] = df['remove_user'].apply(lambda x: clean_text(x))
    df.sort_values("remove_symbols", inplace = True)
    df.drop_duplicates(subset ="remove_symbols", keep = 'first', inplace = True)
    
    df.to_csv(f'downloads/{filename}',encoding='utf8', index=False)

def clean_and_stem_csv(path, filename):
    # Store data to variable, and get only the first column
    df = pd.read_csv(f'{path}', encoding = "ISO-8859-1")
    df = pd.DataFrame(df.iloc[:, 0])

    # Function to remove username (starts with '@')
    df['remove_user'] = np.vectorize(remove_pattern)(df, "@[\w]*")

    # Function to remove numbers, symbols, etc.)
    df['remove_symbols'] = df['remove_user'].apply(lambda x: clean_and_stem_text(x))
    df.sort_values("remove_symbols", inplace = True)
    df.drop_duplicates(subset ="remove_symbols", keep = 'first', inplace = True)

    # Remove links, save to new column
    df['tweet_clean'] = df['remove_symbols'].apply(lambda x: clean_and_stem_text(x))

    # Remove duplicates data
    # df.drop_duplicates(keep = 'first', inplace = True)
    df = df.drop(columns=['remove_user', 'remove_symbols'])
    df.loc[df.astype(str).drop_duplicates().index]

    df.to_csv(f'downloads/{filename}',encoding='utf8', index=False)
    
    