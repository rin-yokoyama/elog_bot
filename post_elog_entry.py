from posixpath import join
import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ElogWriter:
	def __init__(self):
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

	def post_entry(self, chan, user, euser, content, ts, files):
		self.driver.get(self.url+'?cmd=New')
		# Attach files
		for file in files:
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
		input_area = self.driver.find_element(by=By.ID, value="Category_0")
		input_area.click()
		self.driver.switch_to.frame(0)
		text_editor = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body")))
		text_editor.click()
		text_editor.clear()
		text_editor.send_keys('Original message posted at '+ ts + '\n' + content + '\n')
		self.driver.save_full_page_screenshot('ss.png')
		# Submit
		self.driver.switch_to.default_content()
		input_area = self.driver.find_element(by=By.XPATH, value='//*[@id="form1"]/table/tbody/tr[5]/td/span/input[2]')
		input_area.click()

	def close(self):
		self.driver.close()

if __name__ == '__main__':
    writer = ElogWriter()