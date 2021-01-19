import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import string
import re


DRIVER_PATH = '/Users/jasmindial/Downloads/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

# read in list of schools pulled from College Scorecard
schools = pd.read_csv("scorecard_college_info_data_latest.csv")


def format_school_name(sch): 
	# clean
	lower = sch.lower()
	clean = lower.replace("'", "")
	# format for url
	final = clean.replace(' ', '-') 
	return final

schools['name_formatted'] = schools['school.name'].apply(lambda x: format_school_name(x))

def create_url(sch):
	url_base = 'https://bigfuture.collegeboard.org/college-university-search/'
	url = url_base + sch
	return url

val_list = []
count = 0 
for s in schools['name_formatted'][:10]:

	#print (s)
	# just for tracking progress
	count += 1
	print (count)

	# make request
	request = create_url(s)
	try: 
		driver.get(request)
	except WebDriverException: 
		try: 
			time.sleep(7)
			driver.get(request)
		except WebDriverException: 
			# mark as disconnected and jump back to loop
			val_list.append('disconnected')
			continue 


	# find and save need met element		
	try: 
		section = driver.find_element_by_id('topFrame')
		element = section.find_element_by_xpath(".//h5[@class='museoFive ltGray copySm marginTop5']")
		text = element.text
		#val = text[:4].strip()
		try: #if it contains a need met element
			val = re.search(".+%", text)[0]
		except: # if element is blank
			val = text
		val_list.append(val) 
		schools.loc[schools.name_formatted == s, 'need_met'] = text[:4]
	
	except NoSuchElementException: 
		try: # try one more time, in case it needs time to load
			time.sleep(7)
			section = driver.find_element_by_id('topFrame')
			element = section.find_element_by_xpath(".//h5[@class='museoFive ltGray copySm marginTop5']")
			text = element.text
			try: 
				val = re.search(".+%", text)[0]
			except: 
				val = text
			val_list.append(val) 
			#schools.loc[schools.name_formatted == s, 'need_met'] = text[:4]

		except NoSuchElementException: 
			val_list.append('not found')
			#schools.loc[schools.name_formatted == s, 'need_met'] = 'not found'

			continue

driver.quit()	


schools['need_met'] = val_list
schools.to_csv("schools_w_needmet_3.csv", index = False)





