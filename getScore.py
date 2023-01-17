import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

webURL = input('webURL: ')

#initialize web driver
service = Service(executable_path="C:/chromedriver")
options = webdriver.ChromeOptions()
options.add_argument('headless')

with webdriver.Chrome(service=service, options=options) as driver:
    #navigate to the url
    driver.get(webURL)
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

for result in results:
    player = result.find_all('td')
    name = player[0].text.split(' @')[0]
    net = int(player[len(player)-1].text)
    print(f'{name}: {net}')
