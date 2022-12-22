from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random

#web = webdriver.Chrome()
while True:
	fehler = 0
	web = webdriver.Firefox()
	print('\n Start Script')
	
	"""Website aufrufen"""
	web.get("https://www.noen.at/niederoesterreich/chronik-gericht/protest-aktionen-noe-klimaschutz-aktivisten-strafen-nehmen-wir-in-kauf-niederoesterreich-print-klima-aktivismus-klimaschutz-klimawandel-florian-wagner-nadja-prankl-letzte-generation-346133086")

	time.sleep(1)
	
	"""Cookies wegdrücken"""
	
	try:
		cookies = web.find_element_by_xpath('/html/body/div[1]/div/div[4]/div[1]/div[2]/button[4]')
		cookies.click()
	except:
		fehler += 1
		print("Fehler beim Cookies wegdrücken.")
	
	time.sleep(2)
	
	"""Ja anwählen"""
	try:
		click_element = web.find_element_by_xpath('/html/body/div[3]/div/div[3]/article/div[3]/div/div/form/div/div/div/ul/li/div[2]/span/ul/li[1]')
		click_element.click()
	except Exception as e:
		fehler +=1
		print("Fehler beim anklicken von ja\n ", e)
	
	time.sleep(0.5)
	
	
	"""Abschicken"""
	try:
		abschicken = web.find_element_by_xpath('/html/body/div[3]/div/div[3]/article/div[3]/div/div/form/div/div/div/div/a')
		abschicken.click()
	except:
		fehler +=1
		print("Fehler beim abschicken")
	
	if fehler > 3:
		raise TypeError("zu viele Fehler aufgetreten. Skript hat nicht funktioniert.")
	
	time.sleep(random.randint(3,20))

	#absenden = web.find_element_by_xpath('/html/body/div[2]/div[1]/article[1]/div[3]/form/div/div/div/div/a/span')
	#absenden.click()

	#time.sleep(random.randint(5,33))
	#web.save_screenshot('screen.png')
	web.quit()
	#s = random.randint(10,40)
	#print('\n Sleep for ')
	#print(s)
	time.sleep(2)
	
"""Cookies löschen"""
# Chrome mit "rm ~/.config/google-chrome/Default/Cookies*"
