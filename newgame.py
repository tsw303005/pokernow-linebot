from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep

webURL = 'https://www.pokernow.club/'
roomOwner = input('owner: ')

#initialize web driver
service = Service(executable_path="C:/chromedriver")
options = webdriver.ChromeOptions()
# options.add_argument('headless')

with webdriver.Chrome(service=service, options=options) as driver:
    driver.get(webURL)
    driver.implicitly_wait(2)
    driver.find_element(By.XPATH, '/html/body/div[2]/section/div[1]/div/a').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/div[1]/input').send_keys(roomOwner)
    driver.implicitly_wait(0.5)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/button').click()
    sleep(1)
    
    print(driver.current_url)
