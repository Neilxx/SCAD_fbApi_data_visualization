# -*- coding: utf-8 -*-
import urllib.request
import unicodedata
import json
from collections import Counter
from bokeh.charts import Bar, output_file, show, Donut
from bokeh.layouts import column
from bokeh.charts.attributes import cat, color
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app_id = "334263470276709" # Get app id form your control panel
app_secret = "8f7cf3da6c0f1c707c693ce2f3b644bd" # Get app secret form your control panel # DO NOT SHARE WITH ANYONE!
access_token = app_id + "|" + app_secret #Mi
trump_page_id = "153080620724" # Specfic id of fans page
clinton_page_id = "889307941125736"
post_id = "889307941125736_1320311824692010"
facebook_API_url = "https://graph.facebook.com/v2.8"

# HTTP request function
def request_until_succeed(url):
    req = urllib.request.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print("Error ", e)
            #Error handle and retry after 5 sec
            time.sleep( 5 )
            print( "Error for URL %s: %s " % (url, datetime.datetime.now()) )
            print( "Retrying." )

    return response.read().decode('utf8')

# Given page id, and the function  will return 10 post ids before 2016/11/8
def getFacebookPagePostId(page_id, access_token):
    # API append from url
    base = facebook_API_url
    node = "/%s/posts" % page_id
    fields = "?fields=created_time"
    parameters = "&access_token=%s" % (access_token)
    limit = "&limit=10" 
    until = "&until=1478563200"
    url = base + node + fields + parameters + limit + until
    post_ids = []
    datas = json.loads(request_until_succeed(url)) # Send Http Request and get JSON result
    for data in datas['data']:
        post_ids.append(data['id'])
    return post_ids # Show result

# Given post id, and the function  will return 100 comments' messages 
def getFacebookPageCommentData(post_id, access_token):
    # API append from url
    base = facebook_API_url
    node = "/%s/comments" % post_id
    fields = "?fields=message"
    parameters = "&access_token=%s" % (access_token)
    limit = "&limit=100"
    url = base + node + fields + parameters + limit# combine url

    comments = []
    # retrieve data
    datas = json.loads(request_until_succeed(url)) # Send Http Request and get JSON result
    for data in datas['data']:
        comments.append(data['message'])
    return comments

# Given a list of sentences, the function will turn each messages into compound values
# using SentimentIntensityAnalyzer()
def multiSentimentAnalyzer(sentences):
    compounds = []
    S = SentimentIntensityAnalyzer()
    sentiments = map(S.polarity_scores, sentences)
    for sentiment in sentiments:
        compounds.append(sentiment['compound'])
    return compounds

# The function will count the number of different type classified in tellPosNeg()
def countPosNeg(compounds):
    collect = Counter()
    for compound in compounds:
        label = tellPosNeg(compound)
        collect[label] += 1
    collect['pos'] = collect['pos_1'] + collect['pos_2'] + collect['pos_3'] \
                   + collect['pos_4'] + collect['pos_5'] + collect['pos_6'] \
                   + collect['pos_7'] + collect['pos_8']        
    return collect

# The function will classify a list of compound values into different type:
# 'neg', 'pos_1', 'pos_2' ...
def tellPosNeg(compound):
    if compound < 0:
        return 'neg'
    elif 0 <= compound < 0.125:
        return 'pos_1'
    elif 0.125 <= compound < 0.25:
        return 'pos_2'
    elif 0.25 <= compound < 0.375:
        return 'pos_3'
    elif 0.375 <= compound < 0.5:
        return 'pos_4'
    elif 0.5 <= compound < 0.625:
        return 'pos_5'
    elif 0.625 <= compound < 0.75:
        return 'pos_6'
    elif 0.75 <= compound < 0.875:
        return 'pos_7'
    else:
        return 'pos_8'

# The function will transger a number into a string with percentage count
def getDonutName(num):
    return 'Positive ' + str(num/1000) + '%'


if __name__ == '__main__':
    clinton_post_ids = getFacebookPagePostId(clinton_page_id, access_token)
    trump_post_ids = getFacebookPagePostId(trump_page_id, access_token)

    # Get each post's comments, transfer messages into sentiment compound,
    # and store it into values array, which has the counting number of neg and pos
    clinton_values, trump_values =[], []
    for i in range(10):
        clinton_comment_messages = getFacebookPageCommentData(clinton_post_ids[i], access_token)
        clinton_compounds = multiSentimentAnalyzer(clinton_comment_messages)
        clinton_values.append(countPosNeg(clinton_compounds))
        trump_comment_messages = getFacebookPageCommentData(trump_post_ids[i], access_token)
        trump_compounds = multiSentimentAnalyzer(trump_comment_messages)
        trump_values.append(countPosNeg(trump_compounds))

    # Generating the list used to build the dataframe
    clinton_pos, clinton_neg = [], []
    clinton_all_values = [0] * 9
    for value in clinton_values:
        clinton_pos.append(value['pos'])
        clinton_neg.append(-value['neg'])
        clinton_all_values[0] += value['neg']
        clinton_all_values[1] += value['pos_1']
        clinton_all_values[2] += value['pos_2']
        clinton_all_values[3] += value['pos_3']
        clinton_all_values[4] += value['pos_4']
        clinton_all_values[5] += value['pos_5']
        clinton_all_values[6] += value['pos_6']
        clinton_all_values[7] += value['pos_7']
        clinton_all_values[8] += value['pos_8']
    clinton_all_names = list(map(getDonutName, clinton_all_values))
    clinton_all_names[0] = 'Negative ' + str(clinton_all_values[0]/1000) + '%'

    trump_pos, trump_neg = [], []
    trump_all_values = [0] * 9
    for value in trump_values:
        trump_pos.append(value['pos'])
        trump_neg.append(-value['neg'])
        trump_all_values[0] += value['neg']
        trump_all_values[1] += value['pos_1']
        trump_all_values[2] += value['pos_2']
        trump_all_values[3] += value['pos_3']
        trump_all_values[4] += value['pos_4']
        trump_all_values[5] += value['pos_5']
        trump_all_values[6] += value['pos_6']
        trump_all_values[7] += value['pos_7']
        trump_all_values[8] += value['pos_8']
    trump_all_names = list(map(getDonutName, trump_all_values))
    trump_all_names[0] = 'Negative ' + str(trump_all_values[0]/1000) + '%'

    # Formating the dataframe, and feed it into char
    df1 = pd.DataFrame({ 'name' : pd.Series(trump_all_names),
                         'value' : pd.Series(trump_all_values)})
    trump_donut = Donut(df1, label='name', values='value', title='Donald Trump', legend=False, 
                        color=color('name', palette=['#BEBEBE', '#FFD2D2', '#FF9797', '#FF5151', '#FF0000', '#CE0000', '#930000', '#600000', '#4D0000']))

    df2 = pd.DataFrame({ 'name' : pd.Series(clinton_all_names),
                         'value' : pd.Series(clinton_all_values)})
    clinton_donut = Donut(df2, label='name', values='value', title='Hillary Clinton', legend=False, 
                        color=color('name', palette=['#BEBEBE', '#D2E9FF', '#ACD6FF', '#84C1FF', '#46A3FF', '#0080FF', '#0066CC', '#004B97', '#000079']))

    df3 = pd.DataFrame({ 'name' : 'Trump',
                         'post_id' : pd.Series(list(range(1,21,2))),
                         'value' : pd.Series(trump_pos),
                         'type' : 'pos'})

    df4 = pd.DataFrame({ 'name' : 'Trump',
                         'post_id' : pd.Series(list(range(1,21,2))),
                         'value' : pd.Series(trump_neg),
                         'type' : 'neg'})

    df5 = pd.DataFrame({ 'name' : 'Clinton',
                         'post_id' : pd.Series(list(range(2,22,2))),
                         'value' : pd.Series(clinton_pos),
                         'type' : 'pos'})

    df6 = pd.DataFrame({ 'name' : 'Clinton',
                         'post_id' : pd.Series(list(range(2,22,2))),
                         'value' : pd.Series(clinton_neg),
                         'type' : 'neg'})

    df = pd.concat([df3, df4, df5, df6])

    bar = Bar(df, label='post_id', values='value', title='Donald Trump vs. Hillary Clinton', stack='type', legend=False,
              color=color(['name', 'type'], palette=['gray', 'blue', 'gray', 'red']),
              tooltips=[('name', '@name')])

    # Output the html files with charts
    output_file("hw5.html")   
    show(column(bar, trump_donut, clinton_donut))