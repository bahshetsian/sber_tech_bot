import nltk


#russian_stemmer = nltk.stem.SnowballStemmer('russian')
english_stemmer = nltk.stem.SnowballStemmer('english')

def wordFilterStemmer(excluded,wordrow):

    filtered = [english_stemmer.stem(word.lower())
                    for word in wordrow
                    if word.lower() not in excluded
                    and len(word)>1]
    return filtered

def data_clean(dataset, manual_stopwords):
    """
    remove not word character
    """
    tokenizer = nltk.tokenize.RegexpTokenizer(r'[a-zA-Z]+')
    wordrow = tokenizer.tokenize(dataset)
    wordrow_nostopwords = wordFilterStemmer(manual_stopwords,wordrow)
    return wordrow_nostopwords
