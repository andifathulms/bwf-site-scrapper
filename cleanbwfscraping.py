# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 21:57:02 2021

@author: LENOVO
"""

#from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import csv
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def timeCounter(start):
    now = time.perf_counter()
    return f"{now-start:0.5f}"

def requestURL(url):
    print("Request adress...")
    start = time.perf_counter()
    
    for attempt in range(1,11):
        try:
            print(f"Attempt no: {attempt} ...")
            req = requests.get(url,timeout=20, headers={'User-Agent': 'Mozilla/5.0','Connections':'close'})
            print(f"Success! Time : {timeCounter(start)} \n")
            print(req.history)
            return req.content
        except:
            print(f"Fail! Time : {timeCounter(start)} \n")
            time.sleep(0.25)
            continue
        break
    print("Fail! Reached maximum attempt")

def requestHeadless(url):
    options = Options()
    options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    #options.headless = True
    driver = webdriver.Chrome("C:\\Users\\LENOVO\\chromedriver.exe", options = options)
    print("Request URL..")
    driver.get(url)
    return driver.page_source
    
"""   
def openURL(url):
    print("Request adress...")
    start = time.perf_counter()
    for attempt in range(1,6):
        try:
            print(f"Attempt no: {attempt} ...")
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            web = urlopen(req, timeout=30)
            print(f"Success! Time : {timeCounter(start)} \n")
            return web
        except:
            print(f"Fail! Time : {timeCounter(start)} \n")
            continue
        break
    print("Fail! Reached maximum attempt")

def readURL(web):
    print("Reading from URL...")
    start = time.perf_counter()
    for attempt in range(1,6):
        try:
            print(f"Attempt no: {attempt} ...")
            webpage = web.read()
            print(f"Success! Time : {timeCounter(start)} \n")
            return webpage
        except:
            #not work / useless
            print(f"Fail! Time : {timeCounter(start)} \n")
            continue
        break
    print("Fail! Reached maximum attempt")
"""
#separate the name, seed, and country
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
    return ["Q" for i in range(32)]
def roundGS():
    return ["GS" for i in range(16)]

def writeFileSingle(file):
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

def writeFileDouble(file):
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
    

file_dict_WTF = {
                    0:"MSmatches.csv",1:"MSmatches.csv",2:"MSmatches.csv",
                    3:"WSmatches.csv",4:"WSmatches.csv",5:"WSmatches.csv",
                    6:"MDmatches.csv",7:"MDmatches.csv",8:"MDmatches.csv",
                    9:"WDmatches.csv",10:"WDmatches.csv",11:"WDmatches.csv", 
                    12:"XDmatches.csv",13:"XDmatches.csv",14:"XDmatches.csv",
                }
file_dict_Complete = {
                    0:"MSmatches2019.csv",1:"MSmatches2019.csv",
                    2:"WSmatches2019.csv",3:"WSmatches2019.csv",
                    4:"MDmatches2019.csv",5:"MDmatches2019.csv",
                    6:"WDmatches2019.csv",7:"WDmatches2019.csv",
                    8:"XDmatches2019.csv",9:"XDmatches2019.csv"
                }
file_dict_SSP = {
                    0:"MSmatches2007.csv",
                    1:"WSmatches2007.csv",
                    2:"MDmatches2007.csv",
                    3:"WDmatches2007.csv",
                    4:"XDmatches2007.csv"
                }
file_dict_Custom = {
                    0:"MSmatches2007.csv",1:"MSmatches2007.csv",
                    2:"WSmatches2007.csv",#3:"WSmatches2019.csv",
                    3:"MDmatches2007.csv",#4:"MDmatches2019.csv",
                    4:"WDmatches2007.csv",#7:"WDmatches2019.csv",
                    5:"XDmatches2007.csv",#7:"XDmatches2019.csv"
                }
file_dict_Special = {
                    0:"XDmatches2007.csv",1:"XDmatches2007.csv",
                    2:"XDmatches2007.csv",3:"XDmatches2007.csv",
                    4:"XDmatches2007.csv",5:"XDmatches2007.csv",
                    6:"MSmatches2007.csv",7:"WSmatches2007.csv",
                    8:"MSmatches2007.csv"#,5:"MSmatches2007.csv"
                }
file_dict_NoWDQual = {
                    0:"MSmatches2008.csv",1:"MSmatches2008.csv",
                    2:"WSmatches2008.csv",3:"WSmatches2008.csv",
                    4:"MDmatches2008.csv",5:"MDmatches2008.csv",
                    6:"WDmatches2008.csv",#7:"WDmatches2019.csv",
                    7:"XDmatches2008.csv",8:"XDmatches2008.csv"
                }
urlBase = 'https://bwf.tournamentsoftware.com/sport/draw.aspx?id=FC25AF73-B940-4A0A-A80C-327253D4C1FB&draw='
urls = [f'{urlBase}{index}' for index in [26,27,28,29,5]]

origin = time.perf_counter()
for idx,url in enumerate(urls): #maybe use enumerate?
    #use continue to handle skip
    #if(idx in [0,1,2]):continue
    #catch error list index out of range then continue
    
    #webpage = readURL(openURL(url))
    webpage = requestURL(url)
    #print(url)
    #webpage = requestHeadless(url)
    #html parsing
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
        continue
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
    print(f"Finish arranged data. Time : {timeCounter(start)} \n")
   
    #alternative draw
    file_dict = file_dict_Special
    
    file = file_dict[idx]
    if(idx not in [4]) : roundSelect = roundQual()
    #elif(idx in [1]) : roundSelect = round64()
    else: roundSelect = round64()
    #roundSelect = round32()
    try:
        if( idx in [] ): 
            writeFileSingle(file)
        else: 
            writeFileDouble(file)
            
    except Exception as e:
        print(f"Index {idx} NOT work!\n")
        print(e)
        continue
    
    time.sleep(0.25)

print(f"ALL DONE. TOTAL TIME : {timeCounter(origin)} \n")
    #WELL DONE!
    #ADD SUDIRMAN AND THOMAS UBER
    #MAYBE LEARN SOME SELENIUM?
    #IF SUFFICIENT FIX THE"["
    #WHEN DONE REPLACE ALL [5 [3 [9 [