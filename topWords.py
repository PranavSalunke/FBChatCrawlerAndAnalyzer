# get top X words from a chat history (independent from the topxwords in the json file)
# also does by author

import json
import re
import string
import nltk
import bokeh

def cleanLine(line, removeStopWords):

    if line is None:
        return ""

    # remove punctuation
    punctPattern = re.compile('[%s]' % re.escape(string.punctuation))
    line = line.lower()
    line = re.sub(punctPattern, "", line)

    # remove stopwords
    if removeStopWords:
        stopwords = nltk.corpus.stopwords.words("english")
        splitline = line.split()
        cleanedline = []
        for word in splitline:
            if word not in stopwords:
                cleanedline.append(word)

        line = " ".join(cleanedline)

    return line

def printFormat(topwords):
    # prints in a better format to the console
    # call after getTopWords and pass in the output 

    # find longest word
    mostletters = 0
    highestcount = 0
    for person in topwords:
        for word, count in topwords[person]:
            mostletters = max(len(word), mostletters)
            highestcount = max(count, highestcount)

    wordpad = mostletters
    countpad = len(str(highestcount))
    segmentlen = wordpad + countpad + 5 # segemnt: "| [wordpad] [countpad] |""

    for person in topwords:
        print("%s-"%(person.upper()))
        charcount = 0
        for word, count in topwords[person]:  
            word = word.zfill(wordpad).replace("0"," ")
            count = str(count).zfill(countpad)
            print("| %s %s "%(word, count),end="")
            charcount += segmentlen
            if charcount >= 100:
                print("|")
                charcount = 0
        print("|")



def graphWords(topwords):
    # wordlist is a list of tuples
    pass

def getTopWords(wordCount, topx):
    # call after getWordCounts and pass in the output as wordCount

    topwords = {}

    for key in wordCount.keys():
        topwords[key] = []
        sortedlist = sorted(wordCount[key].items(), reverse=True, key=lambda pair: pair[1])
        topX = sortedlist[0:topx]
        for word in topX:  # populate data with the words
            topwords[key].append((word[0], word[1]))

    return topwords




def getWordCounts(jsonfile,removeStopWords):
    wordCount = {"overallCount":{}} # word: count... person name: {word: count}.. 
    chatdata = None
    with open(jsonfile, "r") as jsonfile:
        chatdata = json.load(jsonfile)

    authors = chatdata["authors"]
    authorIdtoName = {}
    for key in authors.keys():
        authorName = authors[key]["authorName"]
        authorIdtoName[key] = authorName
        wordCount[authorName] = {}

    messages = chatdata["messages"]

    for message in messages:
        authorID = message["author"]
        authorName = authorIdtoName[authorID]
        body = cleanLine(message["text"], removeStopWords)
        # print(authorName + "   -  " + body)
        bodywords = body.split()

        for word in bodywords:
            # update chat wide counts
            wordCount["overallCount"][word] = wordCount["overallCount"].get(word,0) + 1

            # update count for author
            wordCount[authorName][word] = wordCount[authorName].get(word,0) + 1

    return wordCount


# SETTINGS
jsonfile = "chatdata.json"
numberwords = 15
removeStopWords = True # common words in English like "i", "the", "you", etc

wordcounts = getWordCounts(jsonfile,removeStopWords)
topwords = getTopWords(wordcounts, numberwords)
printFormat(topwords)
graphWords(topwords)