from flask import Flask, request, render_template,jsonify
import nltk
from autocorrect import spell
from gensim.summarization import summarize as g_sumn
import requests
import json
from bs4 import BeautifulSoup
import re
import sys
import matplotlib.pyplot as plt
import numpy as np
from nltk.corpus import stopwords


app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


def lower_case(text):
    text1 = text
    text1 = re.sub(r'\.(?=[^ \W\d])', '. ', text1)
    word = text1.lower()
    return word


def sent_tokenize(text):
    text = text
    sent_tokenize = nltk.sent_tokenize(text)
    return sent_tokenize


def word_tokenize(text):
    text = text
    word_tokenize = nltk.word_tokenize(text)
    return word_tokenize


def lemmatize(text):
    from nltk.stem import WordNetLemmatizer
    wordnet_lemmatizer = WordNetLemmatizer()

    text = text
    word_tokens = nltk.word_tokenize(text)
    lemmatized_word = [wordnet_lemmatizer.lemmatize(word) for word in
                       word_tokens]
    lemmatized_sent = " ".join(lemmatized_word)
    return lemmatized_sent


def stemming(text):
    from nltk.stem import SnowballStemmer
    snowball_stemmer = SnowballStemmer('english')

    text = text
    word_tokens = nltk.word_tokenize(text)
    stemmed_word = [snowball_stemmer.stem(word) for word in word_tokens]
    stemmed_sent = " ".join(stemmed_word)
    return stemmed_sent


def remove_tags(text):
    import re
    text = text
    cleaned_text = re.sub('<[^<]+?>', '', text)
    return cleaned_text


def remove_numbers(text):
    text = text
    remove_num = ''.join(c for c in text if not c.isdigit())
    return remove_num


def remove_punct(text):
    from string import punctuation
    def strip_punctuation(s):
        return ''.join(c for c in s if c not in punctuation)

    text = text
    text = strip_punctuation(text)
    return text


def remove_stopwords(text):
    from nltk.corpus import stopwords
    stopword = stopwords.words('english')
    text = text
    word_tokens = nltk.word_tokenize(text)
    removing_stopwords = [word for word in word_tokens if word not in stopword]
    sent = " ".join(removing_stopwords)
    return sent


def keyword(text):
    text = text
    word = nltk.word_tokenize(text)
    pos_tag = nltk.pos_tag(word)
    chunk = nltk.ne_chunk(pos_tag)
    NE = [" ".join(w for w, t in ele) for ele in chunk if isinstance(ele, nltk.Tree)]
    return NE


def summarize(text):
    text = text
    sent = nltk.sent_tokenize(text)
    if len(sent) < 2:
        summary1 =  "please pass more than 3 sentences to summarize the text"
    else:
        summary = g_sumn(text)
        summ = nltk.sent_tokenize(summary)
        summary1 = (" ".join(summ[:2]))
    result = summary1
    return result



def plot_top_stopwords_barchart(text):
    stop=set(stopwords.words('english'))
    corpus=nltk.word_tokenize(text)
    from collections import defaultdict
    dic=defaultdict(int)
    for word in corpus:
        if word in stop:
            dic[word]+=1
            
    top=sorted(dic.items(), key=lambda x:x[1],reverse=True)[:10] 
    x,y=zip(*top)
    plt.bar(x,y)
    import uuid
    filename1 = uuid.uuid4().hex
    url1='/home/archman/Desktop/FLASK/NLP-Flask-Website/static/images/'+str(filename1)+'.png'
    plt.savefig(url1)
    url1='static/images/'+str(filename1)+'.png'
    return url1

    
####################################YOUTUBE############################################
def youtuber(video):
    try:
        y=get_transcript(video)
        return y
    except:
        return "Error. Wrong video link perhaps?"


def get_transcript_url(video):
    r = requests.get(video)
    soup = BeautifulSoup(r.content, "lxml")
    title = soup.find("meta", itemprop="name")["content"]
    for i in soup.body.findAll(text=re.compile('TTS_URL'))[0].split('\n'):
        if 'TTS_URL' in i:
            TTS_URL = i.split('"')[1].replace('\\', '').replace('u0026', '&')
            return TTS_URL, title
    return False


def get_transcript(video):
    url, title = get_transcript_url(video)
    extra = "&kind&fmt=srv1&lang=en"
    extra2 = "&kind=asr&fmt=srv1&lang=en"
    texty=""
    if url:
        r = requests.get(url+extra)
        if len(r.text) == 0:
            r = requests.get(url+extra2)
        soup2 = BeautifulSoup(r.content, "lxml")
        if soup2:
            print("Transcription of '{}'".format(title))
            print("-------")
            for line in soup2.text.replace("&#39;", "'").replace('i&#39;', "'").replace('&gt;', '>').split("\n"):
                texty=texty+" "+str(line)
                print(texty)
            return(texty)
    else:
        return 'No subtitles available. Sorry.'


@app.route('/youtube', methods=["GET", "POST"])
def youtube():
    if request.method =='POST':
        url = request.form['url']
        data=youtuber(url)
        low=lower_case(data)
        words=word_tokenize(low)
        sent=sent_tokenize(low)
        remtags=remove_tags(low)
        remstop=remove_stopwords(remtags)
        rempunc=remove_punct(remstop)
        lem=lemmatize(rempunc)
        stem=stemming(lem)
        keywords=keyword(data)
        summ=summarize(low)
        url1=plot_top_stopwords_barchart(low)

        
        return render_template('youtube.html',data=data,keywords=keywords,url1=url1) 
    else:
        return render_template('youtube.html')    


if __name__ == '__main__':
    app.run(debug=True)

