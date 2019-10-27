# All the settings in one place!
# look for the file you want to change the setting for, change it, save this file, and run that program


#  NOTE: THIS IS NOT IMPLEMENTED YET. You have to change the seetings in the individual files for now


# chatCrawler.py

chatCrawer = {
    "outfile": "chatdata.json",  # will be overwritten
    "createMessageIdLists": False,  # to make message id lists for authors and unsent  (If True, json file can get large)
    "xwords": 100,  # the most common words that arent stopwords: https://en.wikipedia.org/wiki/Stop_words
    "numberMessages": None,  # number of messages to get before stopping; None to do all messages
}

# plotMessages.py

plotMessages = {
    "freq": "T"  # list of times: https://stackoverflow.com/a/17001474
    # S - second; T- minute; H - hour; D - day; W - week; M - month; A - year; can do 5T for 5 minutes
}

# textExtractor.py

textExtractor = {
    "printToConsole": False,  # goes faster if this is False
    "jsonfilename": "chatdata.json",
    "outputfilename": "messagetext.txt",
    "csvfilename": "messagetext.csv"  # put None for no csv
}

# topWords.py

topWords = {
    "jsonfile": "chatdata.json",
    "numberwords": 15,
    "removeStopWords": True,  # common words in English like "i", "the", "you", etc
    "graphWords": True,
    "graphOverall": False,  # only matters if graphWords = True
}

# doubleMsg.py

doubleMsg = {
    "jsonfile": "chatdata.json",
    "minCutOff": 5,  # The threshold for a double message in minutes
    "createGraph": True
}
