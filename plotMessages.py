import json
import csv
import pandas as pd
import datetime
from bokeh.plotting import figure, output_file, show, save
from bokeh.palettes import Category10, Plasma256
import matplotlib.pyplot as plt
import time


# plots the messages onto a timeline
# uses the json file created by chatCrawler or the csv created by textExtractor

def makeTimelinePlotJSON(jsonfilename):
    tslist = []
    alist = []
    with open(jsonfilename, "r") as chatdatafile:

        chatdata = json.load(chatdatafile)
        timestamps = chatdata["timestamps"]
        for ts in timestamps:
            timestamp = ts["timestamp"]
            humanreadabletime = datetime.datetime.fromtimestamp(int(timestamp)/1000.0)
            tslist.append(humanreadabletime)
            author = ts["authorName"]
            alist.append(author)

    print(len(tslist))

    # plt.plot(tslist, alist)
    # plt.show()

# ==================================
# =========== CSV HELPER ===========


def makeAggregateDF(df, timestampCol, countCol, freq):
    # makes the smaller data frame given the freqency, count and timetamp column names
    msgCountsDF = df[[timestampCol, countCol]].copy()
    msgCountsDF.index = msgCountsDF[timestampCol]
    return msgCountsDF.resample(freq).sum()


def getFreqName(freq):
    name = freq  # returns freq if unknown
    # remove digits if present
    clean = "".join([i for i in freq if not i.isdigit()]).strip()
    # S - second; T- minute; H - hour; D - day; W - week; M - month; A - year

    if clean == "S":
        name = "second(s)"
    elif clean == "T":
        name = "minute(s)"
    elif clean == "H":
        name = "hour(s)"
    elif clean == "D":
        name = "day(s)"
    elif clean == "W":
        name = "week(s)"
    elif clean == "M":
        name = "month(s)"
    elif clean == "A":
        name = "year(s)"

    return name


def graphTotalOnlyLine(chatmessageDF, timestampCol, freq):
    countCol = "Count"
    msgCountsDF = makeAggregateDF(chatmessageDF, timestampCol, countCol, freq)

    # graph it
    # note you will have to remove the html files yourself

    freqname = getFreqName(freq)
    t = "%s grouped by %s vs counts for all messages" % (timestampCol, freqname)
    plot = figure(x_axis_type='datetime', plot_width=800, plot_height=500, title=t)
    plot.xaxis.axis_label = "%s time" % (timestampCol)
    plot.yaxis.axis_label = "Count"
    plot.line(x=timestampCol, y=countCol, source=msgCountsDF, line_width=2, color="black")
    output_file("plotMessages_Total.html")
    show(plot)


def graphAuthorsLine(chatmessageDF, timestampCol, freq, graphTotal=False):
    uniqueAuthors = list(chatmessageDF["AuthorName"].unique())
    authorCountColNames = []
    # make counts per author on the row (1 if that author, 0 if not)
    for author in uniqueAuthors:
        colName = "".join([i.lower().capitalize() for i in author.split()])+"Count"
        authorCountColNames.append(colName)
        chatmessageDF[colName] = chatmessageDF["AuthorName"].apply(lambda a: 1 if a == author else 0)
        # print(colName)

    # put all authors on one graph
    freqname = getFreqName(freq)
    t = "%s grouped by %s vs counts by author" % (timestampCol, freqname)
    plot = figure(x_axis_type='datetime', plot_width=800, plot_height=500, title=t)
    plot.xaxis.axis_label = "%s time" % (timestampCol)
    plot.yaxis.axis_label = "Count by Author"
    if graphTotal:
        msgCountsDF = makeAggregateDF(chatmessageDF, timestampCol, "Count", freq)
        plot.line(x=msgCountsDF.index, y=msgCountsDF["Count"], line_width=2, alpha=0.2, color="black", legend="Total")

    colorsToUse = Category10[10] if len(uniqueAuthors) <= 10 else Plasma256
    for countCol, color in zip(authorCountColNames, colorsToUse):
        msgCountsDF = makeAggregateDF(chatmessageDF, timestampCol, countCol, freq)
        plot.line(x=msgCountsDF.index, y=msgCountsDF[countCol], line_width=2, alpha=0.6, color=color, legend=countCol)

    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"
    output_file("plotMessages_Authors.html")
    show(plot)


def makeTimelinePlotCSV(csvfilename):
    with open(csvfilename, "r") as chatmessagescsv:
        chatmessageDF = pd.read_csv(chatmessagescsv)

        # convert int to timestamp object. the csv has it in milliseconds. This will be in UTC
        chatmessageDF["TimestampUTC"] = pd.to_datetime(chatmessageDF["Timestamp"], unit="ms")
        # chatmessageDF["TimestampPST"] = chatmessageDF["TimestampUTC"].dt.tz_localize(tz="PST8PDT")  # dont think this actually works
        # add a column for the count of messages per row (just 1)
        numRows = len(chatmessageDF.index)
        chatmessageDF["Count"] = [1]*numRows  # column of 1s

        # aggregate by time. need to make new data frame

        freq = "T"  # list of times: https://stackoverflow.com/a/17001474
        # S - second; T- minute; H - hour; D - day; W - week; M - month; A - year; can do 5T for 5 minutes

        # total counts
        timestampCol = "TimestampUTC"
        graphTotalOnlyLine(chatmessageDF, timestampCol, freq)

        # counts by author
        graphAuthorsLine(chatmessageDF, timestampCol, freq, graphTotal=True)


makeTimelinePlotCSV("messagetext_100.csv")
# makeTimelinePlotJSON("chatdata_100.json")
