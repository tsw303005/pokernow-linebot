from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep

class Pokernow(object):
    
    def __init__(self):
        self.__service = Service(executable_path="C:/chromedriver")
        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument('headless')
        self.__pokernowURL = 'https://www.pokernow.club/'
        
    def getScore(self, url):
        with webdriver.Chrome(service=self.__service, options=self.__options) as driver:
            #navigate to the url
            driver.get(url)
            driver.implicitly_wait(2)
            #find element by id
            driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[6]/div/button').click()
            driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[2]/div/div[2]/div[2]/button[3]').click()
            result = driver.find_element(By.CLASS_NAME, 'ledger-rows').get_attribute('innerHTML')
            soup = BeautifulSoup(result, 'html.parser')
            
        # parse all player's net
        results = soup.find_all('tr')
        # remote last element
        results.pop()

        scoreboard = dict()
        for result in results:
            player = result.find_all('td')
            name = player[0].text.split(' @')[0]
            net = int(player[len(player)-1].text)
            scoreboard[name] = net
            
        return scoreboard
    
    def createNewGame(self, owner):
        with webdriver.Chrome(service=self.__service, options=self.__options) as driver:
            driver.get(self.__pokernowURL)
            driver.implicitly_wait(2)
            driver.find_element(By.XPATH, '/html/body/div[2]/section/div[1]/div/a').click()
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/div[1]/input').send_keys(owner)
            driver.implicitly_wait(0.5)
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/button').click()
            sleep(1)   
            url = driver.current_url

        return url

    