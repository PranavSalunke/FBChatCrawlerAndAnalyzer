#  Facebook Messenger/Chat Crawler and Analyzer


## Table of Contents

* [Intro](#intro)
* [Details](#details)
    * [Modifications needed for you to use this](#modifications-needed-for-you-to-use-this)
    * [Output](#output)
    * [Running the program](#running-the-program)
    * [Basic Structure](#basic-structure)
    * [Many Messages](#many-messages)
* [Other functions](#other-functions)
    * [settings.py](#settingspy)
    * [textExtractor.py](#textextractorpy)
    * [plotMessages.py](#plotmessagespy)
    * [topWords.py](#topwordspy)
    * [doubleMsg.py](#doublemsgpy)
* [Inspiration](#inspiration)



## Intro
First and foremost, I as the programmer can not have access to your Facebook information via this project. Anything this code produces is only on your local computer as a file.


I call this a crawler very loosely. The summary of this program is that it goes through the messages of one chat in Facebook, aggregates some counts, and crates a JSON file with the messages and counts for you to view. Also does some very, very basic analysis. 


I use the fbchat API to request messages: https://fbchat.readthedocs.io/en/stable/index.html


Check below about getting many messages (10000+)

## Details

There are two main files part of this project: `chatCrawler.py` and `userinfo.py`.


`userinfo.py` is the one with your login information and the chat details you want to analyze. This file has important information and is *not* tracked by git. You can find what you need to fill out in `userinfo_template.py`. Make sure to rename it when filled.
If you do not know the Id of the person or group, just put that as `None` and put the name of the person or group. The script will find the id for you and continue on.


`chatCrawler.py` is the bulk (...99%) of this project. It does some checks, and things but as a user, you just need to think about these few lines at the bottom. 


Check other functions below for more scripts that works off the json created by the crawler.


### Modifications needed for you to use this

There are a couple lines at the bottom that act as the "Settings". 


`outfile` is the variable in which the name of the json file is kept


`xwords` is the number of words you want to look at. For instance if you put 10, it shows you the top 10 most frequently used words in your chat along with how many times


`numberMessages` The number of messages to read. Put `None` to read the entire chat. It reads from bottom to top, but is reversed so we see it correctly

`createMessageIdLists` make message id lists for authors and unsent  (If True, json file can get large).


### Output

The output is a json file with the name given in the `outfile` variable.  It is created automatically and is overwritten if you run it again without changing the name. 


Look below for a basic structure of the json object. 


###  Running the program
This was made with the intent of running via the console. After all edits have been made run it with this command (or whatever works on your computer)


`py -3 chatCrawler.py`


`python3 chatCrawler.py`


Output will come to your console and a file will be created with the name you provided. 


### Basic Structure


Look at the output for the full object

```
{
    "messageCount":number,
    "chatName":"name",
    "chatID":"9999999999",
    "messageCount":100,
    "messages": [{<json-ized Message Object>}, ...],
    "authors":{authorID:{data}, author2ID:{data}, ...},
    "attachments": {count: number, <some other counts>},
    "unsent": {count: number, <counts by user>},
    "timestamps": [{timestamp, authorid, authorname}...],
    "mentions" {count, {counts per person mentioned}...}:,
    "reactions": {count, counts per reaction type},
    "topXwords": [(word, count), ...]
    "wordCount": {authorid: {authorname, total words from cleaned messages},...}
    
}
```

NOTE: "topXwords" is not the actual field. X is replaced by the number you put in `xwords` to make "top10words" or "top124words", etc


### Many messages
I have now fixed the issue of getting stuck when asking for a lot of messages by getting them in chunks. However, so that the requests do not look suspicious, there is a delay of 3-15 seconds in between chunks. Each chunk is 10000 messages. It does stop early if you ask for less than 10000, or a number not a multiple of 10000. You can change the chunk size in the `getMessages`method.

The larger the number of total messages you are trying to get, the more time you may have to wait. The progress is displayed onto the console. 

## Other functions


### settings.py

All the settings in one place! Each of the python files have variable that you can change for it to do exactly what you want. In order to make it easier, I have put it all in one file. All you have to do is change it there! No need to ever look at any of the other one (unless you want to of course).

_NOTE: File is present, but not implemented yet. For now, each file's settings (variables) must be changed at the bottom where the settings are indicated with a comment saying `#SETTINGS`_

### textExtractor.py


This script makes a file with the messages in the json file. This is a good way to get a text-only version. A couple settings a the bottom that can be changed in `settings.py`


### plotMessages.py

This script plots the number of messages in the chat vs time. This is done by grouping the counts into time intervals (given by you). It has a method to plot the total number of messages *and* a method to do it by author/chat member. 

There is one "setting" `freq` which is the frequency of the interval. [All values cay be found here](https://stackoverflow.com/a/17001474). However, the useful ones are here as well:


```
S - second
T- minute
H - hour
D - day
W - week
M - month
A - year
```

Note that you can do x minute intervals by doing `xT`.


The plots will be made as html files that will automatically open in your browser. They are interactive and you can play around with the data. The legend is clickable so that it hides different authors so you can get a better view of the others. 


Settings can be changed in `settings.py`

### topWords.py


Prints the most frequently used words to the console. 


This does a similar thing to the `topXwords` in the crawler. This file works on the json created by `chatCrawler`. This allows you to find the top X words *after* you have created the json file. This also allows you to find the top words a particular person has used as well as the top words from the entire chat history. 


There are a couple setting variables at the bottom that can be changed in `settings.py`


Does a simple grouped bar graph as well (if `graphWords = True` in settings)


NOTE: If you request a number of words but one person hasn't sent that many, the graph will still show a "word", but it is in the form of `<initials#>`. Example: If top 100 works were requested but John Doe has only sent 50, the rest of the words will be shown as `<JD1>`...`<JD50>`


### doubleMsg.py

Counts now many times each person "double messaged" and creates a graph.

A double message is when the same person messages a chat after a period of time. 


Example:

```
Person1: hi
person2: hello
X minutes later
person2: anyway what did you want?
```


The settings for this file are just the json file to read from, whether to create the graph, and the value for `X` in minutes. For decent results, keep `X` above 5 minutes. 

Settings can be changed in `settings.py`

## Inspiration


I am in some chats that have a LOT of messages and I wanted to know how many messages we had. But I also wanted to know who sent the most messages, what topics came up most (word count), ect. Some of the things I kept track of like mentions and reactions, only happened once I looked at what was available to me via the fbchat API.

Right now, this only aggregates some minor things and I would love to get into analyzing aspects of the chat. Perhaps find the times we're the most active by the timestamp, or find what sort of attachment is the most popular, or see the sense of our chat by seeing what kinds of reactions we do. I would like to get into the data analysis side a little more, but I think I will need to gather some more data for that. I think this is pretty good for a one-day type of project! :) 