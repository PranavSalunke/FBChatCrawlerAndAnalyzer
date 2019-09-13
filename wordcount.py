# try to find a fast algorithm to find top X words from a large set of words
# Ideally it should be able to to done line by line
# now that I think about it, this is kind of a good interview question

import nltk
import string
import re
import datetime
import pprint

stopwords = nltk.corpus.stopwords.words("english")
punct = string.punctuation


def cleanStr(line):
    # remove punctuation
    punctPattern = re.compile('[%s]' % re.escape(string.punctuation))
    line = re.sub(punctPattern, "", line)
    # remove stopwords
    splitline = line.split()
    cleanedline = []
    for word in splitline:
        if word not in stopwords:
            cleanedline.append(word)
        else:
            print(word)

    return " ".join(cleanedline)

# sort of brute force, memory inefficient


def method1():
    # add all words to a dictionary and their count. Afterwords, sort them and take the top X words

    wordsDict = {}
    with open("lotsofwords.txt", "r") as words:
        for line in words:
            cleanedline = cleanStr(line)
            cleanedsplit = cleanedline.split()

            for word in cleanedsplit:
                currcount = wordsDict.get(word, 0)
                wordsDict[word] = currcount + 1

    # pprint.pprint(wordsDict)


startime = str(datetime.datetime.now())
print("start: %s" % (startime))
method1()
print("start: %s" % (startime))
print("end: " + str(datetime.datetime.now())
