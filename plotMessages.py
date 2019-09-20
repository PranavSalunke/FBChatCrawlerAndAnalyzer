import json
import csv
import pandas as pd
import datetime
import bokeh
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


def makeTimelinePlotCSV(csvfilename):
    with open(csvfilename, "r") as chatmessagescsv:
        chatmessageDF = pd.read_csv(chatmessagescsv)

        # convert int to timestamp object. the csv has it in milliseconds. This will be in UTC
        chatmessageDF["TimestampUTC"] = pd.to_datetime(chatmessageDF["Timestamp"], unit="ms")
        # chatmessageDF["TimestampPST"] = chatmessageDF["TimestampUTC"].dt.tz_localize(tz="PST8PDT")  # dont think this actually works
        # add a column for the count of messages per row (just 1)
        numRows = len(chatmessageDF.index)
        counts = [1]*numRows
        chatmessageDF["Count"] = counts

        # aggregate by time. need to make new data frame

        freq = "T"  # list of times: https://stackoverflow.com/a/17001474
        # S - second; T- minute; H - hour; D - day; W - week; M - month; A - year; can do 5T for 5 minutes

        # total counts
        timestampCol = "TimestampUTC"
        countCol = "Count"
        msgCountsDF = makeAggregateDF(chatmessageDF, timestampCol, countCol, freq)
        # print(msgCountsDF)

        # graph it
        fig, axs = plt.subplots(1, 1)
        axs.set_title("%s grouped by %s vs counts for all messages" % (timestampCol, freq))
        plt.plot(msgCountsDF.index, msgCountsDF["Count"])
        plt.show()

        # counts by author


makeTimelinePlotCSV("messagetext_100.csv")
# makeTimelinePlotJSON("chatdata_100.json")
