# self made crawler to copy/download a partiular chat

import userinfo
import fbchat
from fbchat.models import *
from fbchat import ThreadType
import random
import time
import datetime
import traceback
import pprint
import json
import nltk
#  USE PYTHON 3


# ==========HELPER METHODS==========

def localTimeIsUTC():
    # returns true if local time is utc time
    now = datetime.datetime.now()
    nowutc = datetime.datetime.utcnow()
    nowformated = now.strftime("%A %m/%d/%Y %H:%M")  # example: Thursday 01/24/2019 12:14
    nowutcformated = nowutc.strftime("%A %m/%d/%Y %H:%M")

    return (nowformated == nowutcformated)  # if equal, local time is utc


class CustomClient(fbchat.Client):
    # ==========HELPER METHODS==========
    def buildFrienddict(self):
        users = self.fetchAllUsers()
        tempdict = {}
        tempdict[userinfo.uid] = userinfo.name
        for user in users:
            tempdict[str(user.uid)] = str(user.name)
        return tempdict

    # ==========HELPER METHODS==========


def beginCrawl(outfile):
    # start the fbchat client
    userEmail = userinfo.email
    userPassword = userinfo.pw
    userID = userinfo.uid
    machineLocalIsUTC = localTimeIsUTC()  # detect if local is utc time
    logfileName = "crawler_logfile.txt"
    try:
        client = CustomClient(userEmail, userPassword)
    except fbchat.models.FBchatUserError:
        enterLog(logfileName, "Error logging in")
        exit()

    # update cookie
    with open("cookies.txt", "w") as cookies:
        session_cookies = client.getSession()
        cookies.write("%s\n" % (session_cookies))

    frienddict = client.buildFrienddict()  # can do frienddict["id"] to get the name of the user with that id

    targetChat = userinfo.targetChat
    targetChatId = targetChat["Id"]
    targetChatName = targetChat["Name"]
    targetData = {}

    # fetch a `Thread` object
    thread = client.fetchThreadInfo(targetChatId)[targetChatId]
    targetData["messageCount"] = thread.message_count

    # begin crawl
    safetyLimit = 10  # number of messages to get before stopping. Put message_count for all
    topXwords = 10  # the most common words that arent the common stopwords: https://en.wikipedia.org/wiki/Stop_words
    stopwords = nltk.corpus.stopwords.words("english")

    # Gets the last x messages sent to the thread
    messages = client.fetchThreadMessages(thread_id=targetChatId, limit=safetyLimit)
    # Since the message come in reversed order, reverse them
    messages.reverse()
    targetData["messages"] = messages
    targetData["authors"] = {}  # {authorid: {authorid, author name, count, [list of messageIds]}}
    targetChat["attachments"] = {"count": 0, "sources": {}}  # sources is the source and count per source
    targetChat["unsent"] = {"amount": 0, "authors": {}, messageIds: []}
    targetChat["timestamps"] = []  # [(timestamp, author)...]
    targetChat["mentions"] = {}  # {mentionedID: {count for mentioned, who mentionedID/Name}}
    targetChat["topXwords"] = {}  # {word: count}

    for message in messages:  # process all the messages

        print(message.text)

    print("\n\n  |================|")
    print("  |======DATA======|")
    print("  V================V\n\n")
    pprint.pprint(targetData)

    print("\n\n written to file %s\n" % (outfile))
    with open(outfile, 'w') as outfile:
        json.dump(targetData, outfile)
    client.logout()


outfile = "chatdata.json"  # will be overwritten
beginCrawl(outfile=outfile)
