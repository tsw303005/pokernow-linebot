from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from src.member import Member
import pandas as pd
import requests
import datetime
import os
import json
import csv

class Pokernow(object):
    def __init__(self) -> None:
        # selenium option
        self.__service = Service(executable_path="C:/chromedriver")
        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument('headless')

        # pokernow website
        self.__pokernowURL = 'https://www.pokernow.club/start-game'
        
        # create folder and metadata file
        self.__checkMetaData()

    # make sure that download folder exists, ledger and record folder
    def __checkMetaData(self) -> None:
        self.__fileFolder = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(self.__fileFolder):
            os.makedirs(self.__fileFolder)
            
        self.__ledgerFolder = os.path.join(self.__fileFolder, 'ledgers')
        if not os.path.exists(self.__ledgerFolder):
            os.makedirs(self.__ledgerFolder)
            
        self.__resultFolder = os.path.join(self.__fileFolder, 'results')
        if not os.path.exists(self.__resultFolder):
            os.makedirs(self.__resultFolder)

        self.__scoreboardFile = os.path.join(self.__fileFolder, 'scoreboard.csv')
        if not os.path.exists(self.__scoreboardFile):
            data = pd.DataFrame(columns=Member().GET_ALL_NICKNAME())
            data.to_csv(self.__scoreboardFile)
        
    def __waitForOwner(self, driver) -> None:
        # wait for next
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/p")))
        
        # change room owner
        driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[2]/button').click()
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[1]/div/button[1]').click()
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div/div/button').click()
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/button[1]').click()

    # parse csv to json result, and result players' net
    def __parseCSV(self, filePath) -> dict:
        result = dict()
        with open(filePath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                tmp = result.get(row[0], 0)
                result[row[0]] = tmp + int(row[-1:][0])

        return result
    
    # get roomID
    def __getRoomID(self, url) -> str:
        splitResult = url.split('/')
        roomID = splitResult[-1:][0]

        return roomID

    # download the ledger csv file and store it to local
    # return the file path for parsing later
    def __downloadScore(self, url) -> str:
        # check meta data
        self.__checkMetaData()

        # start to download csv
        roomID = self.__getRoomID(url)
        fileURL = f'{url}/ledger_{roomID}.csv'
        filePath = f'{self.__ledgerFolder}/{roomID}.csv'

        # get csv file
        for i in range(0, 5):
            with requests.get(fileURL, stream=True) as r:
                if r.status_code in [429] and i == 4:
                    raise('[Error]: can not access the csv file')
                elif r.status_code in [429]:
                    sleep(1)
                    continue
                r.raise_for_status()
                with open(filePath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                break 
            
        return filePath

    # check if url exists, then cover the old one
    def __checkURLExist(self, url) -> int:
        # check meta data
        self.__checkMetaData()

        filePath = os.path.join(self.__fileFolder, 'url.txt')
        if not os.path.exists(filePath):
            f = open(filePath, 'w')
            f.close()

        # check if the url exists
        # return game number if exists
        count = 0
        with open(filePath, 'r') as f:
            for i in f.readlines():
                if (i == url):
                    return count

                count += 1


        # if the url is a new one, num++
        with open(filePath, 'a') as f:
            f.write(f'{url}\n')
        
        return count

    # check if someone's name can not found in member list
    def __scanResult(self, data) -> dict:
        nickNames = Member().GET_ALL_NICKNAME()
        result = dict()
        miss = dict()
        result['result'] = dict((i, 0) for i in nickNames)

        for name in data:
            flag = False
            for nickName in nickNames:
                if nickName.lower() in name.lower():
                    result['result'][nickName] = data[name]
                    flag = True
                    break
            if not flag:
                miss[name] = data[name]
        
        if miss:
            result['miss'] = miss

        return result

    # write new result to csv file
    def __appendResultToCSV(self, result, fileName, roomID) -> None:
        self.__checkMetaData()

        data = pd.read_csv(f"{os.path.join(self.__fileFolder, fileName)}", index_col=0)
        data.loc[roomID] = result
        data.to_csv(f"{os.path.join(self.__fileFolder, fileName)}")

    # write miss result
    def __appendMissResult(self, fileName) -> None:
        pass

    # download csv file, append result to csv and return result
    def endGame(self, url) -> str:
        # download the result
        date = datetime.datetime.now().strftime('%Y-%d-%m')
        roomID = self.__getRoomID(url)
        filePath = self.__downloadScore(url)
        
        # parse the csv file to json
        result = self.__parseCSV(filePath)
        data = dict()
        data['date'] = date
        data['roomID'] = roomID
        data['result'] = result

        # scan result to check if someone's name is wrong or missing
        result = self.__scanResult(result)
        if 'miss' in result:
            data['miss'] = result['miss']
        
        # append result to csv file
        self.__appendResultToCSV(result['result'], 'scoreboard.csv', roomID)

        # return result to group
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def settleUp(self) -> str:
        data = pd.read_csv(self.__scoreboardFile, index_col=0)
        total = dict((i, 0) for i in Member().GET_ALL_NICKNAME())
        date = datetime.datetime.now().strftime('%Y-%d-%m')

        members = Member().GET_ALL_NICKNAME()
        for i in members:
            total[i] =int(data[i].sum())
        
        # write to the result
        data.loc["Total"] = total
        data.to_csv(f"{os.path.join(self.__resultFolder, date)}.csv")

        # create new scoreboard csv
        data = pd.DataFrame(columns=Member().GET_ALL_NICKNAME())
        data.to_csv(self.__scoreboardFile)

        return json.dumps(total, indent=2, ensure_ascii=False)
        

    def getScore(self, num) -> str:
       if num >= self.__gameTotal:
           raise Exception('[Error]: the game number does not exist')
       elif not self.__data[num]['ifSettled']:
           raise Exception('[Error]: this game have not settled')
       
       filePath = f'{self.__fileFolder}/ledger_{num}.csv'
       result = self.__parseCSV(filePath)
       jsonStr =  json.dumps(result, indent=2, ensure_ascii=False)
       
       return jsonStr
       
    
    def createNewGame(self) -> str:
        r, w = os.pipe()
        pid = os.fork()
        
        if pid == 0:
            os.close(r)
            w = os.fdopen(w, 'w')
            with webdriver.Chrome(service=self.__service, options=self.__options) as driver:
                driver.get(self.__pokernowURL)
                driver.implicitly_wait(2)
                driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/div[1]/input').send_keys('rrr')
                driver.implicitly_wait(0.5)
                driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/button').click()
                sleep(1)
                url = driver.current_url
                w.write(url)
                w.close()
                self.__waitForOwner(driver)
                
                # record game history
                self.__data[self.__gameTotal] = dict()
                self.__data[self.__gameTotal]["url"] = url
                self.__data[self.__gameTotal]["date"] = datetime.date.today()
                self.__data[self.__gameTotal]['ifSettled'] = False
                self.__gameTotal += 1 

            os._exit(0)

        else:
            os.close(w)
            r = os.fdopen(r)
            url = r.read()
            r.close()
         
            return url


if __name__ == '__main__':
    p = Pokernow()
