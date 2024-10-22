#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import os
import time
import datetime

class Color:
    """Colors class:reset all colors with colors.reset; two sub classes fg for foreground and bg for background; use as colors.subclass.colorname. i.e. colors.fg.red or colors.bg.greenalso, the generic bold, disable, underline, reverse, strike through, and invisible work with the main class i.e. colors.bold"""
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    blinking='\033[05m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    black='\033[30m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'
    purple='\033[35m'
    cyan='\033[36m'
    lightgrey='\033[37m'
    darkgrey='\033[90m'
    lightred='\033[91m'
    lightgreen='\033[92m'
    yellow='\033[93m'
    lightblue='\033[94m'
    pink='\033[95m'
    lightcyan='\033[96m'

def printHelp():
    print """ checkLicenses function to report the availability of licenses
        Usage :
        /path/to/script/checkLicenses.py lic_pat ;#Reports the available licenses for any feature matching lic_pat which should be a regex (beware of the double escapes!)
        /path/to/script/checkLicenses.py -all ;#Reports all the licenses registered in the server
        /path/to/script/checkLicenses.py -list ;#Lists all the features registered in the server
        /path/to/script/checkLicenses.py [-help] ;#Prints this help

        Pro Tip: add this alias to your .cshrc "alias checkLicenses \"lmstat -a > .lic; /path/to/script/checkLicenses.py\" for the easy way

        Example :
            checkLicenses ICCompilerII
            checkLicenses ICCom.*
            checkLicenses ICC
    """

licFile = os.path.expanduser("~/.lic")

reFeatureOk = re.compile(r"Users of ([-\w\d]+):\s+\(Total of (\d+) licenses? issued;\s+Total of (\d+) licenses? in use\)")
reFeatureFuture = re.compile(r"Users of ([-\w\d]+):\s+\(Warning: (\d+) licenses?, future start date\)")
reFeatureNok = re.compile(r"Users of ([-\w\d]+):\s+\(Error: (\d+) licenses?,\s+unsupported by licensed server\)")
reReservation = re.compile(r"\s*\d+\s+RESERVATION[s]* for .*")
reUser = re.compile(r"(.*),\s+start\s+\w+\s+(\d+\/\d+)\s+(\d+:\d+)")
reUserQueued = re.compile(r"(.*)\squeued for (\d+) licenses?")

lics = dict()

def printFeature(feat):
    """Print the feature in a fancy way relatively to the information gatherd with lmstat"""
    #if the dict has something at the adress it means it is supported by the server
    if lics[feat]:
        nbLic, nbInUse, users = lics[feat]
        #Get the number of users
        nbUser = len(users)
        #Get the number of free licenses
        freeLics = int(nbLic) - int(nbInUse)
        #Plural for free licenses
        licPlural = "" if (freeLics==1 or freeLics==-1) else "s"
        #Plural for nb of licenses
        licsPlural = "" if (int(nbLic)==1) else "s"
        #indicate if licenses are available
        if freeLics > 0:
            print Color.green + feat + Color.reset + " is available. " + Color.green + str(freeLics)+ Color.reset + " license"+ licPlural +" free out of " + nbLic
        elif freeLics < 0:
            print Color.blue + feat + Color.reset + " is not available yet. " + Color.blue + str(-freeLics)+ Color.reset + " license"+ licPlural +" will be available"
        else :
            print Color.red + feat + Color.reset + " is not available. "+Color.red+ nbLic + Color.reset + " license"+licsPlural + " in use."

        if users:
            for user in users :
                #Use the regex to retrieve relevant informations
                m = reUser.match(user)
                if m :
                    startDate = m.group(2)+"/" + str(datetime.date.today().year)
                    startYearDay = time.strptime(startDate,"%m/%d/%Y").tm_yday
                    startHour = int(m.group(3).split(":")[0])
                    startMin = int(m.group(3).split(":")[1])
                    currYearDay = time.localtime(time.time()).tm_yday
                    currHour = time.localtime(time.time()).tm_hour
                    currMin = time.localtime(time.time()).tm_min
                    elapsedMin = (currMin - startMin) if (currMin>=startMin) else (currMin - startMin +60)
                    elapsedHrs = (currHour - startHour) if (currHour>=startHour) else (currHour - startHour +24)
                    elapsedHrs = (elapsedHrs) if (currMin>=startMin) else (elapsedHrs -1)
                    elapsedDay = (currYearDay - startYearDay) if (currYearDay>=startYearDay) else (currYearDay - startYearDay + 365)
                    elapsedDay = (elapsedDay) if (currHour>=startHour) else (elapsedDay -1)
                    elapsedTime = ""
                    if elapsedDay:
                        elapsedTime+="%2dD " % elapsedDay
                    else:
                        elapsedTime+="    "
                    if elapsedHrs:
                        elapsedTime+="%2dh " % elapsedHrs
                    else:
                        elapsedTime+="    "
                    elapsedTime+="%2dm" % elapsedMin
                    print("  Since %-10s (%s) --> %s" % (((startDate + " ") if elapsedDay else "") + m.group(3), elapsedTime, m.group(1) ))
                else :
                    m = reUserQueued.match(user)
                    if m:
                        print (Color.red + Color.blinking + "  QUEUED " + Color.reset + m.group(1) + " for " + m.group(2) + " license" + ("" if int(m.group(2)==1) else "s") )
                    else:
                        m = reReservation.match(user)
                        if not m:
                            print "-E- Unrecognized line : " + user
                            continue
                        print (Color.orange + "  RESERVED:        " + Color.reset +  user  )

    else:
        #If feat has an empty entry, it means the the feature is no longer supported
        print Color.red + feat +Color.reset + " is "+Color.red + Color.blinking +"unsupported" + Color.reset+" by license server"
#Warning .lic file must have been created before calling this script
if os.path.isfile(licFile) :
    with open(licFile) as fh:
        for line in fh:
            #If the feature is here
            mOk = reFeatureOk.match(line)
            #match the user reporting line
            mUser = reUser.match(line)
            mUserQueued = reUserQueued.match(line)
            mReservation = reReservation.match(line)
            #If the feature is no longer supported
            mFuture = reFeatureFuture.match(line)
            mNok = reFeatureNok.match(line)
            if mOk:
                #Add an endtry and the relevant informations
                current_feature = mOk.group(1)
                lics[current_feature] = [mOk.group(2),mOk.group(3),list()]
            if mUser or mUserQueued:
                #Users are added to the last entry added
                lics[current_feature][2].append(line.strip())
            if mReservation:
                #Reservation entry added
                lics[current_feature][2].append(line.strip())
            if mNok:
                #Add an empty entry
                lics[mNok.group(1)] = None
            if mFuture:
                lics[mFuture.group(1)] =[-int(mFuture.group(2)),0,list()]
    #Clean .lic file
    os.remove(licFile)
    #Parse argument
    if len(sys.argv) == 1:
        #No args : print help
        printHelp()
        quit(0)
    args = sys.argv[1:]
    if len(args) == 1:
        #One arg can be a utility switch
        if args[0] == "-all":
            #Report all gathered features
            for feat in sorted(lics.keys()):
                printFeature(feat)
            quit(0)
        if args[0] == "-list":
            #Lists all available features (in columns depending on the size of the terminal)
            features = list(sorted(lics.keys()))
            #Get the number of columns in the terminal
            rows, columns = os.popen('stty size', 'r').read().split()
            #Get the maximum length of the feature names and add a padding
            col_width = max(len(word) for word in features) + 2
            #Deduce the number of columns
            nb_col = int(columns)/int(col_width)
            idx = 0
            data_rows = list()
            while idx < len(features):
                #Arrange data in sublists of nb_col elements
                if idx%nb_col == 0:
                    data_rows.append(list())
                data_rows[idx/nb_col].append(features[idx])
                idx += 1
            for line in data_rows:
                #Print the list
                 print "".join(word.ljust(col_width) for word in line)
            quit(0)
        if args[0] == "-help":
            #Ask for help, get help
            printHelp()
            quit(0)
    for arg in args :
        if arg not in ["-all", "-list", "-help"] :
            #For each other argument :
            matchingFeat = set()
            reFeat = re.compile(".*"+arg+".*",re.IGNORECASE)
            #Check if expr match the feature list
            for feat in lics.keys():
                if reFeat.match(feat):
                    matchingFeat.add(feat)
            #Print it sorted
            for feat in sorted(matchingFeat):
                printFeature(feat)
            if not len(matchingFeat) :
                print "-W- No feature matching '"+arg+"'"

else :
    print "-E- cannot find license file. Please do 'lmstat -a > .lic' before calling me ヽ(ಠ_ಠ)ノ"
    quit(1)

