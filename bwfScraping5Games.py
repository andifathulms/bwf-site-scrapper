# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:45:38 2021

@author: LENOVO
"""

import time
import re
import requests
import csv
from bs4 import BeautifulSoup as soup
from collections import Counter
import concurrent.futures

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

def returnidxQual(qlist):
    qualRe = re.compile(r'Qual')
    qualList = [ len(qualRe.findall(q)) for q in qlist ] #search for qual draw
    qualidx = [idx for idx,value in enumerate(qualList) if value == 1] #return the index of qual
    return qualidx

def returnidxGS(qlist):
    qualRe = re.compile(r'Group')
    qualList = [ len(qualRe.findall(q)) for q in qlist ] #search for gs draw
    qualidx = [idx for idx,value in enumerate(qualList) if value == 1] #return the index of gs
    return qualidx

def returnFileList(draw):
    eventList = [draw[i].text[:2] for i in range(len(draw))]#return the event in list
    dictFile = { "MS" : "MSmatches2014(5G).csv","WS" : "WSmatches2014(5G).csv",
             "MD" : "MDmatches2014(5G).csv","WD" : "WDmatches2014(5G).csv",
             "XD" : "XDmatches2014(5G).csv" }
    fileList = [dictFile[i] for idx,i in enumerate(eventList)]
    return fileList

def playersDividerL(player):
    P1 = player[0]
    if len(player) == 2 : P2 = player[1]
    p1 = P1[:-8] if P1.count("[") == 2 else P1[:-5]
    seed = P1[-7] if P1.count("[") == 2 else ""
    c1 = P1[-4:-1]
    p2 = P2[:-5] if len(player) == 2 else ""
    c2 = P2[-4:-1] if len(player) == 2 else ""
    
    playerlist = [p1.strip(), c1.strip(),
                  p2.strip(), c2.strip(), seed.strip()]
    return playerlist

def playersDividerNoCountryL(player):
    P1 = player[0]
    if len(player) == 2 : P2 = player[1]
    p1 = P1[:-3] if P1.count("[") == 1 else P1
    seed = ""
    c1 = ""
    p2 = P2 if len(player) == 2 else ""
    c2 = ""
    
    playerlist = [p1.strip(), c1.strip(),
                  p2.strip(), c2.strip(), seed.strip()]
    return playerlist

def playersDividerR(player):
    P1 = player[0]
    if len(player) == 2 : P2 = player[1]
    p1 = P1[5:-3] if P1.count("[") == 2 else P1[5:]
    seed = P1[-2] if P1.count("[") == 2 else ""
    c1 = P1[1:4]
    p2 = P2[5:] if len(player) == 2 else ""
    c2 = P2[1:4] if len(player) == 2 else ""
            
    playerlist = [p1.strip(), c1.strip(),
                  p2.strip(), c2.strip(), seed.strip()]
    return playerlist

def playersDividerNoCountryR(player):
    P1 = player[0]
    if len(player) == 2 : P2 = player[1]
    p1 = P1[:-3] if P1.count("[") == 1 else P1
    seed = ""
    c1 = ""
    p2 = P2 if len(player) == 2 else ""
    c2 = ""
            
    playerlist = [p1.strip(), c1.strip(),
                  p2.strip(), c2.strip(), seed.strip()]
    return playerlist

#separate the score
def scoreDivider(score):
    game = []
    point = []
    retiredRe = re.compile(r'Retired')
    setsRe = re.compile(r'\d+\-\d+')
    sets = setsRe.findall(score)
    ret = retiredRe.findall(score)
    for i in range(0,5):
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

#list of rounds
def round64():
    rounds = []
    for i in range(63):
        if(i < 32): rounds.append("R64")
        elif(i < 48): rounds.append("R32")
        elif(i < 56): rounds.append("R16")
        elif(i < 60): rounds.append("QF")
        elif(i < 62): rounds.append("SF")
        else: rounds.append("F")
    return rounds
def roundQual():
    return ["Q" for i in range(128)]
def roundGS():
    return ["GS" for i in range(16)]

def writeFileSingle(file,package,idx):
    readyPlayerL = package[0]
    readyPlayerR = package[1]
    roundSelect = package[2]
    readyScore = package[3]
    readyDate = package[4]
    tournament = package[5]
    bwftour = package[6]
    date = package[7]
    players_left = package[8]
    durations = package[9]
    scores = package[10]
    
    with open(file, mode="a", newline="", errors="replace") as file:
        start = time.perf_counter()
        print("Open " + str(file))
        csvwriter = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        for i in range(len(players_left)):
            csvwriter.writerow([date[i],roundSelect[len(roundSelect) - len(players_left) + i],
                                readyPlayerL[i][0],readyPlayerL[i][1],readyPlayerL[i][4],
                                readyScore[i][0][0],readyScore[i][0][1],
                                readyScore[i][0][2],readyScore[i][0][3],readyScore[i][0][4],readyScore[i][2],
                                readyPlayerR[i][0],readyPlayerR[i][1],readyPlayerR[i][4],
                                durations[i],tournament,bwftour,
                                readyScore[i][1][0],readyScore[i][1][1],
                                readyScore[i][1][2],readyScore[i][1][3],
                                readyScore[i][1][4],readyScore[i][1][5],
                                readyScore[i][1][6],readyScore[i][1][7],
                                readyScore[i][1][8],readyScore[i][1][9],scores[i],
                                readyDate[i][0],readyDate[i][1],readyDate[i][2],readyDate[i][3],i])

    file.close()
    print("Close " + str(file))
    print(f"Index {idx} work! Write time : {timeCounter(start)} \n")

def writeFileDouble(file,package,idx):
    readyPlayerL = package[0]
    readyPlayerR = package[1]
    roundSelect = package[2]
    readyScore = package[3]
    readyDate = package[4]
    tournament = package[5]
    bwftour = package[6]
    date = package[7]
    players_left = package[8]
    durations = package[9]
    scores = package[10]
    
    with open(file, mode="a",newline="", errors="replace") as file:
        start = time.perf_counter()
        print("Open " + str(file))
        csvwriter = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        for i in range(len(players_left)):
            
            csvwriter.writerow([date[i],roundSelect[len(roundSelect) - len(players_left) + i],
                                readyPlayerL[i][0],readyPlayerL[i][2],
                                readyPlayerL[i][1],readyPlayerL[i][3], 
                                readyPlayerL[i][4],
                                readyScore[i][0][0],readyScore[i][0][1],
                                readyScore[i][0][2],readyScore[i][0][3],readyScore[i][0][4],readyScore[i][2],
                                readyPlayerR[i][0],readyPlayerR[i][2],
                                readyPlayerR[i][1],readyPlayerR[i][3],
                                readyPlayerR[i][4],
                                durations[i],tournament,bwftour,
                                readyScore[i][1][0],readyScore[i][1][1],
                                readyScore[i][1][2],readyScore[i][1][3],
                                readyScore[i][1][4],readyScore[i][1][5],
                                readyScore[i][1][6],readyScore[i][1][7],
                                readyScore[i][1][8],readyScore[i][1][9],scores[i],
                                readyDate[i][0],readyDate[i][1],readyDate[i][2],readyDate[i][3],i])

    file.close()
    print("Close " + str(file))
    print(f"Index {idx} work! Write time : {timeCounter(start)} \n")
    
def scrapingContent(url,idx):
    webpage = requestURL(url,f'Index - {idx}')
    start = time.perf_counter()
    page_soup = soup(webpage, "html.parser")
    print(f"Parsing HTML. Time : {timeCounter(start)} \n")
    
    #fetch the data
    print("Fetch data...")
    start = time.perf_counter()
    tournament = page_soup.header.find("h2").text
    bwftour = page_soup.header.find("ul").text.strip('\n')
    containers = page_soup.findAll("table", {"class":"matches"})
    try:
        match_containers = containers[0].find("tbody").findChildren("tr", recursive=False)
    except IndexError:
        print(f'Nothing here on index {idx}. \nSkip to next index\n')
        #continue
    players_left = []
    players_right = []
    player_left = []
    player_right = []
    scores = []
    durations = []
    date = []
    
    
    for match_container in match_containers:
        row_containers = match_container.findChildren("td", recursive=False)
        try:
            
            #fill score
            cell_scores = row_containers[5]
            scores.append(cell_scores.text)
            
            #fill duration
            cell_duration = row_containers[8]
            durations.append(cell_duration.text)
            
            #fill date
            cell_date = row_containers[1]
            date.append(cell_date.text)
            
            #fill players
            cell_containers_left = row_containers[2].table.findChildren("tr")
            try:
                cell_containers_right = row_containers[4].table.findChildren("tr")
            except:
                cell_containers_right = []
                cell_containers_right.append("[BYE] BYE")
                if(len(cell_containers_left) == 2): 
                    cell_containers_right.append("[BYE] BYE")
            
            pair = True if(len(cell_containers_left) == 2) else False
            
            #looping for left side    
            for cell_CL in cell_containers_left:
                player_left.append(cell_CL.text.strip().replace('\n',''))
                if(pair and len(player_left) == 1):
                    continue
                else:
                    players_left.append(player_left)
                    player_left = []
    
            try:
            #looping for right side        
                for cell_CR in cell_containers_right:
                    player_right.append(cell_CR.text.strip().replace('\n',''))
                    if(pair and len(player_right) == 1):
                        continue
                    else:
                        players_right.append(player_right)
                        player_right = []
            except:
                for cell_CR in cell_containers_right:
                    player_right.append(cell_CR)
                    if(pair and len(player_right) == 1):
                        continue
                    else:
                        players_right.append(player_right)
                        player_right = []
        except:
            continue
    print(f"Finish fetch data . Time : {timeCounter(start)} \n")
    
    #make it ready to write
    start = time.perf_counter()
    readyPlayerL = []
    readyPlayerR = []
    readyScore = []
    readyDate = []
    for i in range(len(players_left)):
        readyPlayerL.append(playersDividerL(players_left[i]))
        readyPlayerR.append(playersDividerR(players_right[i]))
        readyScore.append(scoreDivider(scores[i]))
        readyDate.append(dateDivider(date[i]))
    
    file = fileIndex[idx]
    if(idx in qualIndex) : roundSelect = roundQual()
    else: roundSelect = round64()
    package = [readyPlayerL,readyPlayerR,roundSelect,readyScore,readyDate,tournament,
           bwftour,date,players_left,durations,scores]
    print(f"Finish arranged data. Time : {timeCounter(start)} \n")
    try:
        if( idx in range(single) ): 
            writeFileSingle(file,package,idx)
        else: 
            writeFileDouble(file,package,idx)
            
    except Exception as e:
        print(f"Index {idx} NOT work!\n")
        print(e)
        #continue
    
    time.sleep(0.25)
#url page

listURL = ["https://bwf.tournamentsoftware.com/sport/draws.aspx?id=039748F1-AA5F-4682-86C6-5A82F1F40712"]
"""
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=0710D060-80C5-4DF6-B379-10606E5D1C18",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=A799C5CE-E413-49BB-B689-EA18FD57518A",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=B82FB7BB-160F-4347-97F2-201BC9631433",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=C1358BD9-8A4E-44B3-AAAD-DF58A7C1B7A2",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=2A427F63-192F-47AA-A821-AFFB78D141BA",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=1C23EB69-7778-43B6-BC35-AC9AB64B4FD9",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=7C25BC15-D06F-4D77-A07B-37B3D2CDDC55",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=41052FEC-16D2-42FC-913C-98D48C99EB46",
           "https://bwf.tournamentsoftware.com/sport/draws.aspx?id=EC86A240-5A66-4B14-B5BD-B7093EE3E314"]"""

realorigin = time.perf_counter()
for idxmain,mainURL in enumerate(listURL):
#def doWebScraping(mainURL):
    #if idxmain not in [0,3]: continue
    print(f'Main URL index - {idxmain}\n')
    webpage = requestURL(mainURL,"main URL")
    
    origin = time.perf_counter()
    start = time.perf_counter()
    page_soup = soup(webpage, "html.parser")
    print(f"Parsing HTML. Time : {timeCounter(start)} \n")
    draw = page_soup.find_all("td", attrs={"class":"drawname"})
    urlbase = "https://bwf.tournamentsoftware.com/sport/"
    urldraw = [urlbase + draw[i].a['href'] for i in range(len(draw))]
    urltext = [draw[i].text for i in range(len(draw))] #list of all draw
    qualIndex = returnidxQual(urltext)
    gsIndex = returnidxGS(urltext)
    fileIndex = returnFileList(draw)
    #eventList = [draw[i].text.strip(' - Qualification') for i in range(len(draw))]
    eventList = [draw[i].text[:2] for i in range(len(draw))]
    counter = Counter(eventList)
    single = counter["MS"] + counter["WS"]
    print(f'Finish for main url. Time : {timeCounter(start)}\nNow for the loop\n')
    index = [idxi for idxi,_ in enumerate(urldraw)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrapingContent,urldraw,index)
        
    
    print(f"DONE FOR URL-{idxmain}. TOTAL TIME : {timeCounter(origin)} \n")
    print("###################################################\n")
    time.sleep(2.5)
print(f"ALL DONE. TOTAL TIME : {timeCounter(realorigin)} \n")



#TRY TO SEPARATE FUNCTION WITH MAIN
#MAKE SPECIAL CASE FOR NO COUNTRY, TESTED FIRST WITH THIS