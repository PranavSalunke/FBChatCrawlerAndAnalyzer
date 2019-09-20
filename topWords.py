# get top X words from a chat history (independent from the topxwords in the json file)
# also does by author

import json
import re
import string
import nltk
from bokeh.plotting import figure, show
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource, FactorRange, Legend
from bokeh.palettes import Category10, Plasma256
from bokeh.transform import factor_cmap


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
    segmentlen = wordpad + countpad + 5  # segemnt: "| [wordpad] [countpad] |""

    for person in topwords:
        print("%s-" % (person.upper()))
        charcount = 0
        for word, count in topwords[person]:
            word = word.zfill(wordpad).replace("0", " ")
            count = str(count).zfill(countpad)
            print("| %s %s " % (word, count), end="")
            charcount += segmentlen
            if charcount >= 100:
                print("|")
                charcount = 0
        print("|")


def getInitials(person):
    initial = ""

    if "NOT_IN_FRIEND_LIST" in person or "not_in_friend_list" in person:
        return "N" + person.split("_")[-1]

    for i in person.split():
        initial += i[0]

    return initial


def makeWordsGraph(topwords, numwords, graphOverall):
    # wordlist is a list of tuples
    t = "Top %d words total and by author" % (numwords)
    people = list(topwords.keys())
    if not graphOverall:
        people.remove("Overall Count")

    # create category labels (top 1, top 2,...)
    cats = []
    for i in range(1, numberwords+1):
        cats.append("top %d" % (i))

    # format x axis and counts:
    x = []
    counts = []
    for i, cat in enumerate(cats):
        for person in people:
            nowordcount = 1
            initials = getInitials(person)  # will have issues if two people have the same initials and word in a group

            try:
                word, count = topwords[person][i]
            except IndexError:  # person didnt use these many words
                word, count = ("<%s%d>" % (initials, nowordcount), 0)
                nowordcount += 1

            x.append((cat, "%s (%s)" % (initials, word)))
            counts.append(count)
    # build graph

    source = ColumnDataSource(data=dict(x=x, counts=counts, people=people*numberwords))
    nump = len(people)
    baseColorsToUse = Category10[nump] if nump <= 10 else Plasma256[nump]
    colorsToUse = baseColorsToUse*numberwords  # repeat the colors for the top X words

    plot = figure(x_range=FactorRange(*x), plot_width=1000, plot_height=600, title=t)
    fc = factor_cmap('x', palette=colorsToUse, factors=x)
    plot.vbar(x='x', top='counts', width=0.9, source=source, fill_color=fc, legend="people")

    plot.xaxis.axis_label = "Person Initials (word) by top x grouping"
    plot.yaxis.axis_label = "Count how many times the (word) was used"
    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xaxis.major_label_orientation = 1
    plot.xgrid.grid_line_color = None
    show(plot)


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


def getWordCounts(jsonfile, removeStopWords):
    wordCount = {"Overall Count": {}}  # word: count... person name: {word: count}..
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
            wordCount["Overall Count"][word] = wordCount["Overall Count"].get(word, 0) + 1

            # update count for author
            wordCount[authorName][word] = wordCount[authorName].get(word, 0) + 1

    return wordCount


# SETTINGS
jsonfile = "chatdata_all.json"
numberwords = 10
removeStopWords = True  # common words in English like "i", "the", "you", etc
graphWords = True
graphOverall = False  # only matters if graphWords = True

wordcounts = getWordCounts(jsonfile, removeStopWords)
topwords = getTopWords(wordcounts, numberwords)
printFormat(topwords)
if graphWords:
    makeWordsGraph(topwords, numberwords, graphOverall)
