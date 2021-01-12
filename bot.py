from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
import re
import os.path
from os import path
import sqlite3
import schedule
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException   
import discord_webhook     
#gourav:p
# LEARNIG SELENIUM
# driver= webdriver.Chrome(executable_path="./chromedriver")
# driver.set_window_size(900,900)
# driver.set_window_position(0,0)
# driver.get("https://teams.microsoft.com")
# sleep(2)
# driver.find_element_by_link_text('Enter').click()
# sleep(2)
# driver.find_element_by_id('handleOrEmail').send_keys("tourist")
# driver.find_element_by_class_name('submit').click()

#Allow the chrome options
opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 1, 
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1, 
    "profile.default_content_setting_values.notifications": 1 
  })



credentials={'email':'example@manit.ac.in','password':'pas'}
def login():
	global driver
	print("logging in")
	emailField = driver.find_element_by_xpath('//*[@id="i0116"]')
	emailField.click()
	emailField.send_keys(credentials['email'])
	time.sleep(5)
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Next button
	time.sleep(5)
	passwordField = driver.find_element_by_xpath('//*[@id="i0118"]')
	passwordField.click()
	passwordField.send_keys(credentials['password'])
	time.sleep(5)
	# driver.find_element_by_id('idChkBx_PWD_KMSI0Pwd').click() #remember login
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Sign in button
	time.sleep(2)
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Sign in button
	
	time.sleep(10)#in_Case of Slow internet increase this time 
	#driver.find_element_by_class_name('use-app-lnk').click() #use the app link


def start_browser():

	global driver
	# driver = webdriver.Chrome(chrome_options=opt,service_log_path='NUL')
	driver= webdriver.Chrome(chrome_options=opt, executable_path="./chromedriver")

	# driver.set_window_size(900,900)
	driver.set_window_position(0,0)
	driver.get("https://teams.microsoft.com")

	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

	if("login.microsoftonline.com" in driver.current_url):
		login()

def Create_DB():
	con=sqlite3.connect('my_database.db')
	c=con.cursor()
	cmd="""CREATE TABLE IF NOT EXISTS timetable(class TEXT,start_time TEXT,end_time TEXT,day TEXT)"""
	c.execute(cmd)
	con.commit()
	con.close()
	print('CREATED DATABASE')


def validate_input(regex,inp):
	if not re.match(regex,inp):
		return False
	return True

def validate_day(inp):
	days = ["monday","tuesday","wednesday","thursday","friday"]#change accordingly

	if inp.lower() in days:
		return True
	else:
		return False

#Create TimeTable
def add_timetable():
	if(not(path.exists("my_database.db"))):
			Create_DB()
	op = int(input("1. Add class\n2. Done adding\nEnter option : "))
	while(op==1):
		name = input("Enter class name : ")
		start_time = input("Enter class start time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",start_time)):
			print("Invalid input, try again")
			start_time = input("Enter class start time in 24 hour format: (HH:MM) ")

		end_time = input("Enter class end time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",end_time)):
			print("Invalid input, try again")
			end_time = input("Enter class end time in 24 hour format: (HH:MM) ")

		day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
		while not(validate_day(day.strip())):
			print("Invalid input, try again")
			end_time = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")


		conn = sqlite3.connect('my_database.db')
		c=conn.cursor()

		# Insert a row of data
		c.execute("INSERT INTO timetable VALUES (?,?,?,?)",(name,start_time,end_time,day))

		conn.commit()
		conn.close()

		print("Class added to database\n")

		op = int(input("1. Add class\n2. Done adding\nEnter option : "))



def view_timetable():
	conn = sqlite3.connect('my_database.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		print(row)
	conn.close()
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True



def joinclass(class_name,start_time,end_time):
	global driver

	try_time = int(start_time.split(":")[1]) + 15
	try_time = start_time.split(":")[0] + ":" + str(try_time)

	time.sleep(5)


	classes_available = driver.find_elements_by_class_name("name-channel-type")

	for i in classes_available:
		if class_name.lower() in i.get_attribute('innerHTML').lower():
			print("JOINING CLASS ",class_name)
			i.click()
			if(driver.find_elements_by_class_name('app-svg icons-triangle-right-small icons-rtl-flip')):
				i.click()
			break


	time.sleep(4)


	try:
		joinbtn = driver.find_element_by_class_name("ts-calling-join-button")
		joinbtn.click()
		

	except:
		#join button not found
		#refresh every minute until found
		k = 1
		while(k<=15):
			print("Join button not found, trying again")
			time.sleep(60)
			driver.refresh()
			joinclass(class_name,start_time,end_time)
			# schedule.every(1).minutes.do(joinclass,class_name,start_time,end_time)
			k+=1
		print("Seems like there is no class today.")
		discord_webhook.send_msg(class_name=class_name,status="noclass",start_time=start_time,end_time=end_time)


	time.sleep(4)
	webcam = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
	if(webcam.get_attribute('title')=='Turn camera off'):
		webcam.click()
	time.sleep(1)

	microphone = driver.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
	if(microphone.get_attribute('title')=='Mute microphone'):
		microphone.click()

	time.sleep(5)
	joinnowbtn = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button')
	joinnowbtn.click()
	#Turnoff incoming video[TODO]
	time.sleep(3)
	# driver.find_element_by_class_name('video-stream-container').click()
	driver.find_element_by_class_name('app-svg icons-more app-bar-extra-icons-fill-colors').click()
	#app-svg icons-more app-bar-extra-icons-fill-colors
	driver.find_element_by_class_name('app-svg icons-call-incoming-video-off').click()
	#app-svg icons-call-incoming-video-off
	discord_webhook.send_msg(class_name=class_name,status="joined",start_time=start_time,end_time=end_time)
	
	#now schedule leaving class
	tmp = "%H:%M"

	class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(start_time,tmp)

	time.sleep(class_running_time.seconds)

	driver.find_element_by_class_name("ts-calling-screen").click()


	driver.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click() #come back to homepage
	time.sleep(1)

	driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
	print("Class left")
	discord_webhook.send_msg(class_name=class_name,status="left",start_time=start_time,end_time=end_time)

def sched():
	conn = sqlite3.connect('my_database.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		#schedule all classes
		name = row[0]
		start_time = row[1]
		end_time = row[2]
		day = row[3]

		if day.lower()=="monday":
			schedule.every().monday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="tuesday":
			schedule.every().tuesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="wednesday":
			schedule.every().wednesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="thursday":
			schedule.every().thursday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="friday":
			schedule.every().friday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="saturday":
			schedule.every().saturday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="sunday":
			schedule.every().sunday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))


	#Start browser
	start_browser()
	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		schedule.run_pending()
		time.sleep(1)


if __name__=="__main__":
	# start_browser()
	#joinclass("Cse_699_Test","13:39","13:41")
	op = int(input(("1. Modify Timetable\n2. View Timetable\n3. Start Bot\nEnter option : ")))
	
	if(op==1):
		add_timetable()
	if(op==2):
		view_timetable()
	if(op==3):
		sched()

