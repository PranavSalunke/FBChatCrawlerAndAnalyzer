import csv
import json
import datetime


def extract(jsonfilename, outputfilename, csvfilename, printToConsole):
    with open(jsonfilename, "r") as chatdatafile, open(outputfilename, "w") as justtext:

        csvrows = []
        chatdata = json.load(chatdatafile)
        messages = chatdata["messages"]
        authors = chatdata["authors"]
        authorIdtoName = {}
        for key in authors.keys():
            authorName = authors[key]["authorName"]
            authorIdtoName[key] = authorName

        zpad = len(str(chatdata["messageCount"]))

        messageNumber = 0
        for m in messages:
            messageNumber += 1
            author = authorIdtoName[m["author"]].upper()

            body = m["text"].strip() if m["text"] else ""  # if next is none, make body empty
            body = body if body else "<<empty. Can happen because it was an image, gif, attachment, etc. Message ID: %s>>" % (m["uid"])

            timestamp = m["timestamp"]
            humanreadabletime = datetime.datetime.fromtimestamp(int(timestamp)/1000.0)
            messageNumberStr = str(messageNumber).zfill(zpad)

            if printToConsole:
                print("[%s] %s  %s (%s)\n%s\n" % (messageNumberStr, author, timestamp, humanreadabletime, body))

            # write to file
            try:
                justtext.write("[%s] %s  %s (%s)\n%s\n\n" % (messageNumberStr, author, timestamp, humanreadabletime, body))
            except UnicodeEncodeError:
                body = "<<UnicodeEncodeError on this message. Can happen because of special characters and emojis. Message ID: %s>>" % (m["uid"])
                justtext.write("[%s] %s  %s (%s)\n%s\n\n" % (messageNumberStr, author, timestamp, humanreadabletime, body))

            if csvfilename:
                # header: "AuthorID", "AuthorName", "Message", "Timestamp"
                body = body.replace("\n", "<<\\n>>")
                csvrows.append([m["author"], author, body, timestamp])

        # make csv file
        if csvfilename:
            with open(csvfilename, "w", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                header = ["AuthorID", "AuthorName", "Message", "Timestamp"]
                csvwriter.writerow(header)
                csvwriter.writerows(csvrows)


# SETTINGS
printToConsole = False  # goes faster if this is False
jsonfilename = "chatdata.json"
outputfilename = "messagetext.txt"
csvfilename = "messagetext.csv"  # put None for no csv
extract(jsonfilename, outputfilename, csvfilename, printToConsole)
