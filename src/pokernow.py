from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import requests
import datetime
import os
import json
import csv

class Pokernow(object):
    def __init__(self):
        self.__service = Service(executable_path="C:/chromedriver")
        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument('headless')
        self.__pokernowURL = 'https://www.pokernow.club/start-game'
        self.__fileFolder = os.path.join(os.getcwd(), 'download')
        self.__gameTotal = 0
        self.__data = dict()
        
        with open(f"{os.path.join(os.getcwd(), 'scoreboard.json')}") as f:
            data = json.load(f)
            self.__data = data
            self.__gameTotal = len(data)
        
    def __waitForOwner(self, driver):
        # wait for next
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/p")))
        
        # change room owner
        driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[2]/button').click()
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[1]/div/button[1]').click()
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div/div/button').click()
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/button[1]').click()

    def __parseCSV(self, filePath):
        result = dict()
        with open(filePath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                result[row[0]] = row[-1:][0]

        return result
    
    def __downloadScore(self, url, num):
        splitResult = url.split('/')
        roomID = splitResult[-1:][0]
        fileURL = f'{url}/ledger_{roomID}.csv'
        filePath = f'{self.__fileFolder}/ledger_{num}.csv'

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
    
    def settleGame(self, num):
        if int(num) >= self.__gameTotal:
            raise Exception('[Error]:  the game number does not exist')

        filePath = self.__downloadScore(self.__data[num]['url'], num)
        self.__data[num]['filePath'] = filePath
        self.__data[num]['result'] = self.__parseCSV(filePath)
        self.__data[num]['ifSettled'] = True
        
        # write result back to scoreboard
        with open(f"{os.path.join(os.getcwd(), 'scoreboard.json')}", 'w') as f:
            jsonStr =  json.dumps(self.__data, indent=2, ensure_ascii=False)
            print(jsonStr, file=f)
        
        return self.__data[num]['result']
    
    def settleUp(self, startNum, endNum):
        if startNum > endNum:
            raise Exception('[Error]: start game number should not be greater than end game number')
        elif endNum > self.__gameTotal:
            raise Exception('[Error]: end game number does not exist')
        
        result = dict()
        members = list()
        with open(f"{os.path.join(os.getcwd(), 'member.json')}") as f:
            data = json.load(f)
            
            for member in data["members"]:
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
        

    def getScore(self, num):
       if num >= self.__gameTotal:
           raise Exception('[Error]: the game number does not exist')
       elif not self.__data[num]['ifSettled']:
           raise Exception('[Error]: this game have not settled')
       
       filePath = f'{self.__fileFolder}/ledger_{num}.csv'
       result = self.__parseCSV(filePath)
       jsonStr =  json.dumps(result, indent=2, ensure_ascii=False)
       
       return jsonStr
       
    
    def createNewGame(self):
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
    print(p.settleUp(0, 8))
