# Detect double messages
# A double message is when the same person messages twice after some time without anyone else replying between those messgaes


import json
import datetime
from bokeh.plotting import figure, show


# calculate double messages per person
def calculateDoubleMsg(jsonfile, minCutOff):
    doubleMsgCounts = {}
    cutoffDT = datetime.timedelta(minutes=minCutOff)
    chatdata = None
    with open(jsonfile, "r") as jsonfile:
        chatdata = json.load(jsonfile)

    # init tracking dict
    authors = chatdata["authors"]
    for key in authors.keys():
        authorName = authors[key]["authorName"]
        doubleMsgCounts[authorName] = 0

    lastReadTimestampDT = None
    lastReadAuthor = None
    timestamps = chatdata["timestamps"]
    for entry in timestamps:
        timestamp = entry["timestamp"]  # assumption is that timestamp is in milliseconds (the same as queried in chatCrawler.py)
        authorName = entry["authorName"]
        timestampDT = datetime.datetime.fromtimestamp(timestamp/1000)  # takes seconds

        if lastReadAuthor is not None and lastReadTimestampDT is not None:
            # see if double message
            if authorName == lastReadAuthor:  # same person
                if timestampDT - lastReadTimestampDT > cutoffDT:
                    doubleMsgCounts[authorName] += 1

        lastReadAuthor = authorName
        lastReadTimestampDT = timestampDT

    return doubleMsgCounts


# graph
def graphDoubleMsgs(doubleMsgs):
    authors = []
    counts = []
    for key in doubleMsgs.keys():
        authors.append(key)
        counts.append(doubleMsgs[key])

    p = figure(x_range=authors, plot_height=250, title="Double Messages")
    p.vbar(x=authors, top=counts, width=0.9)
    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    show(p)


# SETTINGS
jsonfile = "chatdata.json"
minCutOff = 5  # The threshold for a double message in minutes
createGraph = True

doubleMsgs = calculateDoubleMsg(jsonfile, minCutOff)
if createGraph:
    graphDoubleMsgs(doubleMsgs)
