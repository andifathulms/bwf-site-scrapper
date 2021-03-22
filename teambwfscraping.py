# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 19:38:59 2021

@author: LENOVO
"""

import time
import re
import requests
import csv
from bs4 import BeautifulSoup as soup
#import concurrent.futures

def timeCounter(start):
    now = time.perf_counter()
    return f"{now-start:0.5f}"

def requestURL(url,arg):
    print(f'Request adress for {arg} ...')
    start = time.perf_counter()
    
    for attempt in range(1,11):
        try:
            print(f"Attempt no: {attempt} ...")
            req = requests.get(url,timeout=20, headers={'User-Agent': 'Mozilla/5.0','Connections':'close'})
            print(f"Success! Time : {timeCounter(start)} \n")
            return req.content
        except:
            print(f"Fail! Time : {timeCounter(start)} \n")
            time.sleep(0.25)
            continue
        break
    print("Fail! Reached maximum attempt")

#separate the score
def scoreDivider(score):
    game = []
    point = []
    retiredRe = re.compile(r'Retired')
    setsRe = re.compile(r'\d+\-\d+')
    sets = setsRe.findall(score)
    ret = retiredRe.findall(score)
    for i in range(0,3):
        try:
            game.append('('+sets[i]+')')
            point.append(game[i].strip("(").strip(')').split("-")[0])
            point.append(game[i].strip("(").strip(')').split("-")[1])
        except:
            game.append("")
            point.append("")
            point.append("")
    
    retired = "Ret" if(len(ret) == 1) else ""
    if(score == "Walkover"): retired = "WO"
    scoreset = [game,point,retired]
    return scoreset

def checkReverse(scoreset):
    flag = False
    if(scoreset[2] != "Ret" or scoreset[2] != "WO"):
        set1 = int(scoreset[1][0]) - int(scoreset[1][1])
        set2 = int(scoreset[1][2]) - int(scoreset[1][3])
        if(scoreset[1][4] != ""): set3 = int(scoreset[1][4]) - int(scoreset[1][5])
        else: set3 = 0
        if(set1 < 0 and set2 < 0):flag = True
        if(set1 < 0 and set3 < 0):flag = True
        if(set2 < 0 and set3 < 0):flag = True
    return flag

def reconstructScore(scoreset):
    P = scoreset[1]
    newP = []
    newP.append(P[1])
    newP.append(P[0])
    newP.append(P[3])
    newP.append(P[2])
    newP.append(P[5])
    newP.append(P[4])
    G = []
    G.append('('+P[1]+'-'+P[0]+')')
    G.append('('+P[3]+'-'+P[2]+')')
    if(P[5] != ""): G.append('('+P[5]+'-'+P[4]+')')
    return [G,newP,scoreset[2]]

def reconstructScoreText(scoreset):
    P = scoreset[1]
    if(P[5] == ""):
        print("IF")
        return f'{P[0]}-{P[1]} {P[2]}-{P[3]}'
    else:
        print("ELSE")
        return f'{P[0]}-{P[1]} {P[2]}-{P[3]} {P[4]}-{P[5]}'

#separate the date
def dateDivider(date):
    timeRe = re.compile(r'\d+:\d\d\s\D\D')
    daymonthRe = re.compile("\d+/")
    t = timeRe.findall(date)
    cleandate = date.strip(t[0]) if(len(t) > 0) else date
    weekday = cleandate[0:3]
    year = cleandate[-4:]
    if (date == ""):
        month = ""
        day = ""
        weekday = ""
        year = ""
    else:
        dm = daymonthRe.findall(date)
        month = dm[0].strip("/")
        day = dm[1].strip("/")
    return [weekday,month,day,year]

urls = [f'https://bwf.tournamentsoftware.com/sport/matches.aspx?id=B4E6AB00-0CE9-489C-9B8F-3F4DCFB8A178&d=201706{i}'
        for i in range(20,25)]

#urls = [f'https://bwf.tournamentsoftware.com/sport/draw.aspx?id=8CAC5EA9-6346-4B74-BF78-CC2FB7A211B3&draw={i}'
#        for i in [9,7,8]]

for idxmain,url in enumerate(urls):
    #if idxmain in [0]: continue
    print(f'Starting for URL - {idxmain}')
    origin = time.perf_counter()
    webpage = requestURL(url,"")
    page_soup = soup(webpage, "html.parser")
    #print(page_soup.find_all("table",attrs={"class":"matches"}))
    row_container = page_soup.find_all("table",attrs={"class":"matches"})[0]
    draw_container = row_container.findChildren("tr")
    length = len(draw_container)
    ##FOR SUDIRMAN START I = 2// i+2
    #draw_container[1].find_all("td",attrs={"class":"nowrap"})[0].a['href']
    match_container = [draw_container[i+1].find_all("td",attrs={"class":"nowrap"})[0].a['href']
                       for i in range(length - 1)]
    urlbase = "https://bwf.tournamentsoftware.com/sport/"
    draws = [urlbase + match_container[i] for i in range(length - 1)]
    tournament = page_soup.header.find("h2").text
    bwftour = page_soup.header.find("ul").text.strip('\n')
    
    event = []
    scores = []
    durations = []
    readyPlayerL = []
    readyPlayerR = []
    readyDate = []
    readyScore = []
    for idx,draw in enumerate(draws):
        #if idx in [0]: continue
        start = time.perf_counter()
        print(f'Request Index-{idx}')
        webpage = requestURL(draw,"")
        print(f'Finish Request.Time: {timeCounter(start)}')
        page_soup = soup(webpage, "html.parser")
        table_container = page_soup.find_all("table",attrs={"class":"matches"})[0]
        date = page_soup.table.tr.text.strip("\n").strip("Time:")
        match_cont = table_container.tbody.findChildren("tr",recursive=False)
        for match in match_cont:
            cell = match.findChildren("td", recursive=False)
            try:
                countryRe = re.compile(r'\[\D\D\D]')
                
                cell_event = cell[1]#1
                #print("1")
                cell_left = cell[2]#2
                #print("2")
                cell_right = cell[4]#4
                #print("3")
                cell_durations = cell[9]
                #print("4")
                """
                #FOR SUDIRMAN ONLY 
                cell_event = cell[0]
                cell_left = cell[1]
                cell_right = cell[3]
                """
                c1 = False
                c2 = False
                try:
                    rescountryL = countryRe.findall(cell_left.text)
                    countryL = rescountryL[0].strip("[").strip("]")
                    c1 = True
                except:
                    countryL = ""
                try:
                    rescountryR = countryRe.findall(cell_right.text)
                    countryR = rescountryR[0].strip("[").strip("]")
                    c2 = True
                except:
                    countryR = ""
                
                #countryL = "" #
                #countryR = "" #
                print("5")
                splitNL = cell_left.text.split("\n")
                splitNR = cell_right.text.split("\n")
                #pair = True if(len(rescountryL) == 2) else False
                pair =  True #
                countryL1 = countryL
                #countryL2 = countryL if pair else ""
                countryR1 = countryR
                #countryR2 = countryR if pair else ""
                
                
                #playerL1 = splitNL[2]
                #playerR1 = splitNR[2]
                #playerL2 = splitNL[4][:-6] if pair else ""
                #playerR2 = splitNR[4][6:] if pair else ""
                """
                try:
                    #playerL2 = splitNL[4][:-6] if pair else ""
                    #playerR2 = splitNR[4][6:] if pair else ""
                    playerL2 = splitNL[4]
                    playerR2 = splitNR[4]
                except:
                    playerL2 = ""
                    playerR2 = ""
                """
                if(c1):
                    try:
                        playerL2 = splitNL[4][:-6] if pair else ""
                        countryL2 = countryL
                    except:
                        playerL2 = ""
                        countryL2 = ""
                    try:
                        playerL1 = splitNL[2][:-6]
                    except:
                        playerL1 = splitNL[2]
                if(c2):
                    try:
                        playerR2 = splitNR[4][6:] if pair else ""
                        countryR2 = countryR
                    except:
                        playerR2 = ""
                        countryR2 = ""
                    try:
                        playerR1 = splitNR[2][6:]
                    except:
                        playerR1 = splitNR[2]
                if(not c1):
                    playerL1 = splitNL[2]
                    try:
                        playerL2 = splitNL[4]
                        countryL2 = countryL
                    except:
                        playerL2 = ""
                        countryL2 = ""
                if(not c2):
                    playerR1 = splitNR[2]
                    try:
                        playerR2 = splitNR[4]
                        countryR2 = countryR
                    except:
                        playerR2 = ""
                        countryR2 = ""
                    
                #PS IM LOSING MY MIND ON THIS, TRY TO FORMALIZE 2MRW
                #PS ITS MESSY BUT ITS WORK
                playerleft = [playerL1,countryL1,playerL2,countryL2,""]
                playerright = [playerR1,countryR1,playerR2,countryR2,""]
                
                cell_scores = cell[5] #5
                #print("6")
                #cell_scores = cell[4] FOR SUDIRMAN ONLY
                ###CHECK THE SCORE###
                csText = cell_scores.text
                scoreset = scoreDivider(csText)
                print(checkReverse(scoreset))
                print(playerleft)
                print(playerright)
                if(checkReverse(scoreset)):
                    print("SWAPPING..")
                    newSc = reconstructScore(scoreset)
                    newScText = reconstructScoreText(newSc)
                    scores.append(newScText)
                    csText = newScText
                    ###SWAP PL X PR
                    
                    temp = playerleft
                    playerleft = playerright
                    playerright = temp
                else:
                    print("NO SWAP")
                    scores.append(csText)
                event.append(cell_event.text)
                durations.append(cell_durations.text)
                #durations.append("") #FOR SUDIRMAN ONLY
                
                print("###")
                print(playerleft)
                print(playerright)
                print("###")
                
            except Exception as e:
                print("Error : " + str(e) + "#NO MATCH. SKIP")
                continue
            readyPlayerL.append(playerleft)
            readyPlayerR.append(playerright)
            readyDate.append(dateDivider(date))
            readyScore.append(scoreDivider(csText))
            
    file = "TEST.csv"
    with open(file, mode="a",newline="", errors="replace") as file:
        start = time.perf_counter()
        print("Open " + str(file))
        csvwriter = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(readyPlayerL)):
            
            csvwriter.writerow([event[i],date,"",
                                readyPlayerL[i][0],readyPlayerL[i][2],
                                readyPlayerL[i][1],readyPlayerL[i][3], 
                                readyPlayerL[i][4],
                                readyScore[i][0][0],readyScore[i][0][1],
                                readyScore[i][0][2],readyScore[i][2],
                                readyPlayerR[i][0],readyPlayerR[i][2],
                                readyPlayerR[i][1],readyPlayerR[i][3],
                                readyPlayerR[i][4],
                                durations[i],tournament,bwftour,
                                readyScore[i][1][0],readyScore[i][1][1],
                                readyScore[i][1][2],readyScore[i][1][3],
                                readyScore[i][1][4],readyScore[i][1][5],scores[i],
                                readyDate[i][0],readyDate[i][1],readyDate[i][2],readyDate[i][3]])

    file.close()
    print("Close " + str(file))
    print(f"Index {idx} work! Write time : {timeCounter(start)} \n")
    time.sleep(0.5)
    
    print(f'Finish URL - {idxmain}.Time: {timeCounter(origin)}\n')