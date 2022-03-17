from posixpath import join
import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class ElogWriter:
	def __init__(self):
		try:
			options = Options()
			options.add_argument('-headless')
			self.driver = webdriver.Firefox(options=options)

			# Sign in to elog
			self.url = os.environ.get("ELOG_URL")
			self.driver.get(self.url)
			input_area = self.driver.find_element(by=By.NAME, value="uname")
			input_area.clear()
			input_area.send_keys(os.environ.get("ELOG_UNAME"))
			input_area = self.driver.find_element(by=By.NAME, value="upassword")
			input_area.clear()
			input_area.send_keys(os.environ.get("ELOG_UPASSWORD"))
			input_area = self.driver.find_element(by=By.NAME, value="remember")
			input_area.send_keys(0)

			input_form = self.driver.find_element(by=By.CLASS_NAME, value="login_submit")
			input_form.click()

			with open('channel2category.json','r') as f:
				self.chan2cat = json.load(f)
			self.init_fail = False
		except:
			self.init_fail = True

	def check_exists_by_xpath(self, xpath):
		try:
			self.driver.find_element(by=By.XPATH, value=xpath)
		except NoSuchElementException:
			return False
		return True

	def post_entry(self, chan, user, euser, content, ts, permalink, files):
		if self.init_fail:
			return None
		try:
			self.driver.get(self.url+'?cmd=New')
			# Attach files
			for file in files:
				if self.check_exists_by_xpath("attfile"):
					return None
				input_area = self.driver.find_element(by=By.NAME, value="attfile")
				input_area.send_keys(file)
				input_area = self.driver.find_element(by=By.XPATH, value='//*[@id="attachment_upload"]/td[2]/input[2]')
				input_area.click()
			# Fill out forms
			input_area = self.driver.find_element(by=By.NAME, value="Author")
			input_area.clear()
			input_area.send_keys(euser + "(Slack)")
			input_area = self.driver.find_element(by=By.NAME, value="Subject")
			input_area.clear()
			input_area.send_keys("Slack post to #" + chan + " by " + user)
			input_area = self.driver.find_element(by=By.NAME, value="Type")
			input_area.send_keys("Info")
			input_area.click()
		except NoSuchElementException:
			return None

		# Check if a category named "Slack" exists		
		# Otherwise, check category 0 to prevent error
		xpath = '//input[@value="Slack"]'
		if self.check_exists_by_xpath(xpath):
			input_area = self.driver.find_element(by=By.XPATH, value=xpath)
		else:
			input_area = self.driver.find_element(by=By.NAME, value="Category_0")
		input_area.click()

		# Check if the channel name exists in the map
		if chan in self.chan2cat:
			xpath = '//input[@value="'+ self.chan2cat[chan] +'"]'
			# Check if the Category checkbox exists
			if self.check_exists_by_xpath(xpath):
				input_area = self.driver.find_element(by=By.XPATH, value=xpath)
				input_area.click()
		# Switching to the iframe containing the text editor
		self.driver.switch_to.frame(0)
		text_editor = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body")))
		# Clear and fill the main text
		text_editor.click()
		text_editor.clear()
		text_editor.send_keys('Original message posted at '+ ts + '\n')
		text_editor.send_keys(permalink + '\n')
		text_editor.send_keys(content + '\n')
		# Take a screenshot for debugging
		self.driver.save_full_page_screenshot('ss.png')
		# Submit
		self.driver.switch_to.default_content()
		try:
			input_area = self.driver.find_element(by=By.XPATH, value='//*[@id="form1"]/table/tbody/tr[5]/td/span/input[2]')
			input_area.click()
		except NoSuchElementException:
			return None
		return self.driver.current_url

	def close(self):
		self.driver.close()

if __name__ == '__main__':
    writer = ElogWriter()