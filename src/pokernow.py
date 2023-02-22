from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from src.member import Member
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
        
        # make sure that download folder exists, ledger and record folder
        self.__fileFolder = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(self.__fileFolder):
            os.makedirs(self.__fileFolder)
            
        self.__ledgerFolder = os.path.join(self.__fileFolder, 'ledgers')
        if not os.path.exists(self.__ledgerFolder):
            os.makedirs(self.__ledgerFolder)
            
        self.__resultFolder = os.path.join(self.__fileFolder, 'results')
        if not os.path.exists(self.__resultFolder):
            os.makedirs(self.__resultFolder)
            
            
        # game number and game data
        self.__num = 0
        self.__data = dict()

        
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
                result[row[0]] = row[-1:][0]

        return result
    
    # download the ledger csv file and store it to local
    def __downloadScore(self, url, num) -> str:
        splitResult = url.split('/')
        roomID = splitResult[-1:][0]
        fileURL = f'{url}/ledger_{roomID}.csv'
        filePath = f'{self.__fileFolder}/ledgers/{num}.csv'

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
        filePath = os.path.join(self.__fileFolder, 'url.txt')
        if not os.path.exists(filePath):
            f = open(filePath, 'w')
            f.close()

        # check if the url exists
        # return game number if exists
        with open(filePath, 'r') as f:
            for i in f.readlines():
                spl = i.split(' ')
                if (spl[0] == url):
                    return int(spl[1])
        
        # if the url is a new one, num++
        with open(filePath, 'a') as f:
            f.write(f'{url} {self.__num}\n')
            
        result = self.__num
        self.__num += 1
        return result
        
    
    # download csv file and calculate the result
    def endGame(self, url) -> dict:
        gameNum = self.__checkURLExist(url)

        # download the result
        filePath = self.__downloadScore(url, gameNum)
        
        # parse the csv file to json
        result = self.__parseCSV(filePath)
        self.__data[gameNum] = dict()
        self.__data[gameNum]['date'] = datetime.date.today().strftime('%Y/%d/%m')
        self.__data[gameNum]['result'] = result
        
        
        # write result back to scoreboard
        with open(f"{os.path.join(self.__fileFolder, 'scoreboard.json')}", 'w') as f:
            jsonStr = json.dumps(self.__data, indent=2, ensure_ascii=False)
            print(jsonStr, file=f)

        
        return json.dumps(self.__data[gameNum]['result'], indent=2, ensure_ascii=False)
    
    def settleUp(self, startNum, endNum) -> str:
        if startNum > endNum:
            raise Exception('[Error]: start game number should not be greater than end game number')
        elif endNum > self.__gameTotal:
            raise Exception('[Error]: end game number does not exist')
        
        result = dict()
        members = list()
        with open(f"{os.path.join(os.getcwd(), 'member.json')}") as f:
            data = json.load(f)
            
            for member in data['members']:
                result[member] = 0
                members.append(member)
        
        for i in range(startNum, endNum+1):
            filePath = f'{self.__fileFolder}/ledger_{i}.csv'
            data = self.__parseCSV(filePath)
            
            for key in data:
                for member in members:
                    if member.lower() in key.lower():
                        result[member] += int(data[key])
                        break
        
        jsonStr =  json.dumps(result, indent=2, ensure_ascii=False)
        return jsonStr
        

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
    p.endGame('https://www.pokernow.club/games/pglXXeL4L06PjQQ73dsnpMXM4')
