# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 15:18:21 2021

@author: LENOVO
"""

import time
import re
import requests
import csv
from bs4 import BeautifulSoup as soup
from collections import Counter
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

def isCancelled(text):
     cancelRe = re.compile(r'Cancel|cancel|CANCEL')
     result = cancelRe.findall(text)
     if(len(result) > 0):
         return True
     else:
         return False

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
                                readyScore[i][0][2],readyScore[i][2],
                                readyPlayerR[i][0],readyPlayerR[i][1],readyPlayerR[i][4],
                                durations[i],tournament,bwftour,
                                readyScore[i][1][0],readyScore[i][1][1],
                                readyScore[i][1][2],readyScore[i][1][3],
                                readyScore[i][1][4],readyScore[i][1][5],scores[i],
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
                                readyScore[i][0][2],readyScore[i][2],
                                readyPlayerR[i][0],readyPlayerR[i][2],
                                readyPlayerR[i][1],readyPlayerR[i][3],
                                readyPlayerR[i][4],
                                durations[i],tournament,bwftour,
                                readyScore[i][1][0],readyScore[i][1][1],
                                readyScore[i][1][2],readyScore[i][1][3],
                                readyScore[i][1][4],readyScore[i][1][5],scores[i],
                                readyDate[i][0],readyDate[i][1],readyDate[i][2],readyDate[i][3],i])

    file.close()
    print("Close " + str(file))
    print(f"Index {idx} work! Write time : {timeCounter(start)} \n")

def getAllTournament(url):
    titles = []
    links = []
    options = Options()
    options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    options.headless = True
    start = time.perf_counter()
    print("Open Driver..")
    driver = webdriver.Chrome("C:\\Users\\LENOVO\\chromedriver.exe", options = options)
    print("Request URL..")
    driver.get(url)
    print(f"Success! Time : {timeCounter(start)} \n")
    for i in range(1,21):
        xpath = f'/html/body/div[1]/section/form/div/div/div[1]/div[1]/div[2]/div/ul/li[{i}]'
        tournaments = driver.find_elements_by_xpath(xpath)
        for tournament in tournaments:
            tour = tournament.find_element_by_class_name("media__link")
            titles.append(tour.text)
            links.append(tour.get_attribute("href").replace("/tournament?","/draws.aspx?"))
        print(f'xpath = {i}')
    return titles,links

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
    dictFile = { "MS" : "MSmatches2007.csv","WS" : "WSmatches2007.csv",
             "MD" : "MDmatches2007.csv","WD" : "WDmatches2007.csv",
             "XD" : "XDmatches2007.csv" }
    fileList = [dictFile[i] for idx,i in enumerate(eventList)]
    return fileList

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
    elif(idx in gsIndex) : roundSelect = roundGS()
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

url = "https://bwf.tournamentsoftware.com/find?DateFilterType=0&StartDate=2007-11-02&EndDate=2007-12-31&page=1&TournamentCategoryIDList%5B0%5D=false&TournamentCategoryIDList%5B1%5D=false&TournamentCategoryIDList%5B2%5D=false&TournamentCategoryIDList%5B3%5D=false&TournamentCategoryIDList%5B4%5D=false&TournamentCategoryIDList%5B5%5D=false&TournamentCategoryIDList%5B6%5D=false&TournamentCategoryIDList%5B7%5D=false&TournamentCategoryIDList%5B8%5D=false&TournamentCategoryIDList%5B9%5D=false&TournamentCategoryIDList%5B10%5D=false&TournamentCategoryIDList%5B11%5D=false&TournamentCategoryIDList%5B12%5D=false&TournamentCategoryIDList%5B13%5D=false&TournamentCategoryIDList%5B14%5D=false&TournamentCategoryIDList%5B15%5D=false&TournamentCategoryIDList%5B16%5D=false&TournamentCategoryIDList%5B17%5D=6&TournamentCategoryIDList%5B18%5D=false&TournamentCategoryIDList%5B19%5D=false&TournamentCategoryIDList%5B20%5D=false&TournamentCategoryIDList%5B21%5D=false&TournamentCategoryIDList%5B22%5D=false&TournamentCategoryIDList%5B23%5D=false&TournamentCategoryIDList%5B24%5D=false&TournamentCategoryIDList%5B25%5D=false&TournamentCategoryIDList%5B26%5D=false&TournamentCategoryIDList%5B27%5D=false&TournamentCategoryIDList%5B28%5D=false&TournamentCategoryIDList%5B29%5D=false&TournamentCategoryIDList%5B30%5D=false"

#CONSIDER UNIVERSITY GAMES
#Check the "Others" Event from recent years
#Look for double at lower year
#AFRICAN GAMES 11 DOWNWARDS
#SEAG09 DOWNWARDS
#Central American Caribbean Games
#South American Games
#AG10 MXD
#IM COUNTING THE UNIV GAMES10
#KEEP RECORD ON OTHER MULTI EVENT
#MIND THE TRUNCATE NAME ON 11
#MAKE A DISTINGUISH FOR W AND L
"""
https://bwf.tournamentsoftware.com/sport/draws.aspx?id=FC25AF73-B940-4A0A-A80C-327253D4C1FB
solve that first things first
"""
titles,links = getAllTournament(url)
print(titles)
print(links)

#loop through all of the link
outerCounter = time.perf_counter()
msg = []
for idxmain,mainURL in enumerate(links):
    
    print(f'Links-{idxmain} : {titles[idxmain]}\n')
    webpage = requestURL(mainURL,"main URL")
    
    #Check if it cancelled
    if(isCancelled(titles[idxmain])):
        msg.append("Cancelled")
        print("This tournament is cancelled, skip to next links...")
        continue
    
    origin = time.perf_counter()
    start = time.perf_counter()
    
    #Parsing HTML
    page_soup = soup(webpage, "html.parser")
    print(f"Parsing HTML. Time : {timeCounter(start)} \n")
    
    #Find all the draw
    try:
        draw = page_soup.find_all("td", attrs={"class":"drawname"})
    except: #catch the error blank
        msg.append("Blank")
        print("This tournament is blank, skip to next links...")
        continue
    
    #Construct the draw links
    urlbase = "https://bwf.tournamentsoftware.com/sport/"
    urldraw = [urlbase + draw[i].a['href'] for i in range(len(draw))]
    urltext = [draw[i].text for i in range(len(draw))] #list of all draw
    
    #Find the qual,groupstage,and file index //need revision
    try:
        qualIndex = returnidxQual(urltext)
        gsIndex = returnidxGS(urltext)
        fileIndex = returnFileList(draw)
        eventList = [draw[i].text[:2] for i in range(len(draw))]
        counter = Counter(eventList)
        single = counter["MS"] + counter["WS"]
    except:
        msg.append("Event name doesnt match")
        print("Event name doesnt match, revise later, skip to next links...")
        continue
    
    print(f'Finish collecting draw URL. Time : {timeCounter(start)}\nNext, Scraping each draw...\n')
    index = [idxi for idxi,_ in enumerate(urldraw)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrapingContent,urldraw,index)
        
    msg.append("Success")   
    print(f"Links-{idxmain} : {titles[idxmain]} Completed\n. TOTAL TIME : {timeCounter(origin)} \n")
    print("###################################################\n")
    time.sleep(0.75)
    
print(f"ALL COMPLETED. TOTAL TIME : {timeCounter(outerCounter)} \n")
for idxtitle,title in enumerate(titles):
    print(f'Link-{idxtitle} # {title} # {msg[idxtitle]}')


