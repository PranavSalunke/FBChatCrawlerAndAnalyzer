# self made crawler to copy/download a partiular chat and gather some data about it
# creates a json file with data about the chat

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
import string
import re
#  USE PYTHON 3


# ==========HELPER METHODS==========
def enterLog(logfileName, message):
    with open(logfileName, "a") as logfile:
        logfile.write("%s\n" % (message))
        print(message)
        logfile.flush()


def localTimeIsUTC():
    # returns true if local time is utc time
    now = datetime.datetime.now()
    nowutc = datetime.datetime.utcnow()
    nowformated = now.strftime("%A %m/%d/%Y %H:%M")  # example: Thursday 01/24/2019 12:14
    nowutcformated = nowutc.strftime("%A %m/%d/%Y %H:%M")

    return (nowformated == nowutcformated)  # if equal, local time is utc


# helper helper method

def getReactionType(message, userid):
    # find coresponding value
    val = message.reactions[userid]
    newval = None

    if val is fbchat.MessageReaction.LOVE:
        newval = "LOVE"
    elif val is fbchat.MessageReaction.SMILE:
        newval = "SMILE"
    elif val is fbchat.MessageReaction.WOW:
        newval = "WOW"
    elif val is fbchat.MessageReaction.SAD:
        newval = "SAD"
    elif val is fbchat.MessageReaction.ANGRY:
        newval = "ANGRY"
    elif val is fbchat.MessageReaction.YES:
        newval = "YES"
    elif val is fbchat.MessageReaction.NO:
        newval = "NO"

    return newval


def makeMessageJSON(messsageObj):
    # NOTE: not perfect since some fields have their own class that I'm not taking into consideration
    # reaction originally was a dict with the reactor and the reaction object. now its just a dict with the reactor and the type as a string
    # attachment is either true or false in the returned dict instead of object
    # attachment is either true or false in the returned dict instead of object
    # some fields will be missing from the original

    msg = {}
    msg["text"] = messsageObj.text
    msg["mentions"] = len(messsageObj.mentions) > 0  # if there are mentions or not
    msg["uid"] = messsageObj.uid
    msg["author"] = messsageObj.author
    msg["timestamp"] = messsageObj.timestamp
    msg["is_read"] = str(messsageObj.is_read)
    msg["read_by"] = messsageObj.read_by  # list
    msg["unsent"] = str(messsageObj.unsent)

    msg["attachments"] = len(messsageObj.attachments) > 0  # if  empty list or not

    # for reactions, must make the value in the dict not an object
    # ex. MessageReaction.WOW -> WOW
    reactKeys = messsageObj.reactions.keys()
    newReactDict = {}
    if len(reactKeys) > 0:  # has reactions. Makes into a list of tuples
        for reactorid in reactKeys:
            newReactDict[reactorid] = getReactionType(messsageObj, reactorid)

    msg["reactions"] = newReactDict
    return msg


def getAttachmentType(attachment):
    # might not have all possibilities. Returns None if type cant be found
    if attachment is fbchat.ShareAttachment:
        return "share"
    elif attachment is fbchat.Sticker:
        return "sticker"
    elif attachment is fbchat.FileAttachment:
        return "file"
    elif attachment is fbchat.AudioAttachment:
        return "audio"
    elif attachment is fbchat.ImageAttachment:
        return "image"
    elif attachment is fbchat.VideoAttachment:
        return "video"
    else:
        return None


def cleanStr(line, stopwords):
    # remove non ascii
    line = line.encode("ascii", "namereplace")
    line = line.decode("ascii")
    # remove punctuation
    punctPattern = re.compile('[%s]' % re.escape(string.punctuation))
    line = re.sub(punctPattern, "", line)
    # remove stopwords
    splitline = line.split()
    cleanedline = []
    for word in splitline:
        if word not in stopwords:
            cleanedline.append(word)

    return " ".join(cleanedline)

# ========END HELPER METHODS=========


class CustomClient(fbchat.Client):
    # ==========HELPER METHODS==========
    def buildFrienddict(self):
        users = self.fetchAllUsers()
        tempdict = {}
        tempdict[userinfo.uid] = userinfo.name
        for user in users:
            tempdict[str(user.uid)] = str(user.name)
        return tempdict


def beginCrawl(outfile, pprintFile, xwords, numberMessages):
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

    topXField = "top%dwords" % (xwords)  # make this top10words or top42words, etc
    targetChat = userinfo.targetChat
    targetChatId = targetChat["Id"]
    targetChatName = targetChat["Name"]
    targetData = {}

    # If id is given, use it. if only name is given, find id
    # this only works with one to one chats and not groups
    if targetChatId is None:
        if targetChatName is None:
            print("ERROR: Give target id or name. If you're trying for a group. You must know the ID")
            client.logout()
            exit()

        for friendId in frienddict:
            friendname = frienddict[friendId]
            if targetChatName == friendname:
                targetChatId = friendId
                break  # id has been found

        if targetChatId is None:  # still None, id was not found
            print("id could not be found by given name. Make sure it is not a Group name")
            client.logout()
            exit()

    # init targetData
    targetData["chatName"] = targetChatName
    targetData["chatID"] = targetChatId
    targetData["messageCount"] = 0
    targetData["messages"] = []  # all the messages; raw messages (Message objects from fbchat converted into dicts)
    targetData["authors"] = {}  # {authorid: {authorid, author name, count, [list of messageIds]}}
    targetData["attachments"] = {"count": 0, "type": {}, "sharesource": {}}  # total and count per type of attachment. if Share, put source as well
    targetData["unsent"] = {"count": 0, "authors": {}, "messageIds": []}  # authors: {author: count}
    targetData["timestamps"] = []  # [{timestamp, authorid and name}...]
    targetData["mentions"] = {"count": 0}  # {total count, mentionedID: {count for mentioned, who mentionedID and count}}
    targetData["reactions"] = {"count": 0}  # {total count, reactions and their count, reactorsID: count for reactions}
    targetData[topXField] = {}  # {word: count}

    # fetch a `Thread` object
    thread = client.fetchThreadInfo(targetChatId)[targetChatId]
    targetData["messageCount"] = thread.message_count

    # begin crawl
    if numberMessages is None:
        numberMessages = thread.message_count  # number of messages to get before stopping. Put message_count for all

    # Gets the last x messages sent to the thread
    messages = client.fetchThreadMessages(thread_id=targetChatId, limit=numberMessages)
    #  message come in reversed order, reverse them
    messages.reverse()

    # process every message
    wordbag = ""
    stopwords = nltk.corpus.stopwords.words("english")
    for message in messages:  # process all the messages
        # print(message) # print message object to console
        if message.text is not None:
            msgTextOrig = message.text
            msgTextClean = cleanStr(message.text, stopwords)  # cleaned
        else:
            msgTextOrig = ""
            msgTextClean = ""

        muid = message.uid
        authorId = message.author  # gives id
        authorName = frienddict[authorId]

        # ## make Message object JSON serializable
        msgJSON = makeMessageJSON(message)
        targetData["messages"].append(msgJSON)

        # ## update authors
        #  {authorid: {authorid, author name, count, [list of messageIds]}}
        existingAuthorDict = targetData["authors"].get(authorId)  # returns None if doesnt exist
        if existingAuthorDict is None:
            # create new entry
            targetData["authors"][authorId] = {"authorId": authorId, "authorName": authorName, "count": 1, "msgIdList": [muid]}
        else:
            # update existing entry
            targetData["authors"][authorId]["msgIdList"].append(muid)
            targetData["authors"][authorId]["count"] += 1

        # ## update attachments
        # {"count": 0, "type": {}}  # type of attachment and count per type. if ShareAttachment, put source as well
        attachmentList = message.attachments
        for attachment in attachmentList:
            targetData["attachments"]["count"] += 1
            attachmentType = getAttachmentType(attachment)
            # possible types: "share", "sticker", "file", "audio", "image", "video", None (not a string)
            currcount = targetData["attachments"]["type"].get(attachmentType, 0)  # 0 if its not there so far
            targetData["attachments"]["type"][attachmentType] = currcount + 1

            if attachmentType == "share":
                currcount = targetData["attachments"]["sharesource"].get(attachment.source, 0)
                targetData["attachments"]["sharesource"][attachment.source] = currcount+1

        # ## update unsent
        # {"count": 0, "authors": {}, "messageIds": []}  # authors: {author: count}
        # True/False; only interested if True
        if message.unsent:
            targetData["unsent"]["count"] += 1

            # update author count who have unsent
            currDict = targetData["unsent"]["authors"].get(authorId)  # returns None if doesnt exist
            if currDict is None:
                # create new entry
                targetData["unsent"]["authors"][authorId] = {"authorId": authorId, "authorName": authorName, "count": 1, "msgIdList": [muid]}
            else:
                # update existing
                targetData["unsent"]["authors"][authorId]["msgIdList"].append(muid)
                targetData["unsent"]["authors"][authorId]["count"] += 1

            targetData["unsent"]["messageIds"].append(muid)

        # ## update timetamps
        # [{timestamp, authorid and name}...]
        msgtimestamp = message.timestamp  # is in unix epoch time
        targetData["timestamps"].append({"timestamp": msgtimestamp, "authorId": authorId, "authorName": authorName})

        # ## update mentions
        # {"count":, mentionedID: {count for mentioned, who mentionedID and count}}
        # mentioned is the one who is being mentioned
        # mentioner is the one doing the mentioning/author (the one who sent the message)

        mentionsList = message.mentions
        for mention in mentionsList:
            mentionedId = mention.thread_id
            targetData["mentions"]["count"] += 1

            currDict = targetData["mentions"].get(mentionedId)  # None if not in the dict yet
            if currDict is None:
                # create new entry
                targetData["mentions"][mentionedId] = {"count": 1, "mentionedBy": {authorId: 1}}
            else:
                # update existing
                targetData["mentions"][mentionedId]["count"] += 1
                currcount = targetData["mentions"][mentionedId]["mentionedBy"].get(authorId, 0)  # return 0 if not there
                targetData["mentions"][mentionedId]["mentionedBy"][authorId] = currcount + 1

        # ## update reactions
        # {"count": 0}  {total count, reactions and their count,reactorsID: count for reactions}
        reactionsDict = message.reactions
        reactionsDictKeys = reactionsDict.keys()
        if len(reactionsDictKeys) > 0:  # has reactions. Makes into a list of tuples
            for reactorid in reactionsDictKeys:
                targetData["reactions"]["count"] += 1
                reactiontype = getReactionType(message, reactorid)
                currcount = targetData["reactions"].get("total" + reactiontype, 0)  # 0 if not there
                targetData["reactions"]["total" + reactiontype] = currcount + 1

                # how many times has this person made a reaction
                currDict = targetData["reactions"].get(reactorid)  # none if not there
                if currDict is None:
                    # make new entry
                    reactorName = frienddict[reactorid]
                    targetData["reactions"][reactorid] = {"count": 1, reactiontype: 1, "reactorID": reactorid, "reactorName": reactorName}
                else:
                    # update entry
                    targetData["reactions"][reactorid]["count"] += 1
                    currcount = targetData["reactions"][reactorid].get(reactiontype, 0)
                    targetData["reactions"][reactorid][reactiontype] = currcount + 1

        # ## update top x words (most complicated if done efficiently)
        # put all the lines here to process later
        wordbag += msgTextClean

    # ##now find the top X words
    stopwords = nltk.corpus.stopwords.words("english")
    wordsDict = {}
    cleanedsplit = cleanStr(wordbag, stopwords).split()

    for word in cleanedsplit:
        currcount = wordsDict.get(word, 0)
        wordsDict[word] = currcount + 1

    # sort the values now. result is a list of tuples
    sortedlist = sorted(wordsDict.items(), reverse=True, key=lambda pair: pair[1])
    topX = sortedlist[0:xwords]
    # print(topX)
    for word in topX:
        targetData[topXField][word[0]] = word[1]

    # ##print out the data
    print("\n\n  |================|")
    print("  |======DATA======|")
    print("  V================V\n\n")
    pprint.pprint(targetData, indent=4)

    print("\n\n===>  written to file %s  <===\n" % (outfile))
    with open(outfile, 'w') as outfile:
        json.dump(targetData, outfile, indent=4)

    # if pprintFile is not None:
    #     print("\n pprint output sent to %s" % (pprintFile))
    #     with open(pprintFile, "w") as pprintFileObj:
    #         # remove all special characters
    #         pformated = pprint.pformat(targetData)
    #         pformated = pformated.encode("ascii", "namereplace")
    #         pformated = pformated.decode("ascii")
    #         # write to file
    #         pprintFileObj.write(pformated)

    client.logout()


# SETTINGS
starttime = str(datetime.datetime.now())

outfile = "chatdata.json"  # will be overwritten
pprintFile = "chatdataPPrint.txt"  # None to print to stdout
xwords = 10  # the most common words that arent the common stopwords: https://en.wikipedia.org/wiki/Stop_words
numberMessages = 20  # None to do all messages
beginCrawl(outfile=outfile, pprintFile=pprintFile, xwords=xwords, numberMessages=numberMessages)


endtime = str(datetime.datetime.now())
print("starttime: %s\nendtime %s" % (starttime, endtime))
