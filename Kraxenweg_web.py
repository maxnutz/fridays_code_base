from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random

#web = webdriver.Chrome()
while True:
	web = webdriver.Firefox()
	print('\n Start Script')
	
	web.get("https://m.noen.at/krems/wegen-gutachten-hotelprojekt-in-der-kremser-innenstadt-ist-gestorben-krems-innenstadt-krems-hotelprojekt-kremser-bank-christian-hager-gutachten-print-287300483")

	time.sleep(random.randint(4,20))
	
	#cookies = web.find_element_by_xpath('//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')
	#cookies.click()
	
	#time.sleep(2)
	
	gruenraum = web.find_element_by_xpath('/html/body/div/div/div[2]/div/div/div[1]/div[3]/div/div[2]/div/div[2]')
	gruenraum.click()
	time.sleep(random.randint(3,20))

	#absenden = web.find_element_by_xpath('/html/body/div[2]/div[1]/article[1]/div[3]/form/div/div/div/div/a/span')
	#absenden.click()

	time.sleep(random.randint(5,33))
	#web.save_screenshot('screen.png')
	web.quit()
	s = random.randint(10,40)
	print('\n Sleep for ')
	print(s)
	time.sleep(s)
