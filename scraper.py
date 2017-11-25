# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib2 import urlopen
import requests
import logging
import re
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
import datetime


class doubanMovieComments(object):
	def __init__(self, userName, passWord, captcha_solution='', captcha_id=''):
		self.user = userName
		self.pw = passWord
		self.captcha_solution = captcha_solution
		self.captcha_id = captcha_id
		self.login_session = self.auth()
		
	def parseCaptcha(self, landingPage):
		img = landingPage.find('img',{'id':'captcha_image'})
		link = img.attrs['src']
		captcha_id = link.split('id=')[1][:-7]
		return {'pic':link, 'id':captcha_id}

	def auth(self):
		s = requests.session()
		if self.captcha_solution == '':
			login_data = {'form_email':self.user, 
		              	      'form_password':self.pw,
		                      'remember':'on'}
		else:
			login_data = {'form_email':self.user, 
				      'form_password':self.pw,
				      'captcha-solution': self.captcha_solution,
                                      'captcha-id': self.captcha_id,
                                      'remember':'on'}

		postRequest = s.post('https://accounts.douban.com/login',
			              data = login_data)
		landingPage = BeautifulSoup(postRequest.text,'lxml')
		if landingPage == 'Please try later.':
			raise Exception(
				{"Please try later.": "douban block your login attempt."}
				)
		elif u'验证码不正确' in landingPage.prettify():
 			captcha = self.parseCaptcha(landingPage)
			raise Exception(
				{
				"try verification combination": {captcha['id']:captcha['pic']}
				}
				)
		else:
			logging.warning("login successfully.")
			return s

	def logout(self):
		self.login_session.get(
			'https://www.douban.com/accounts/logout?source=main&ck=7lKz'
		)
		logging.warning("logout session ends.")

	def loadComments(self, movieId, start=0, verify=False):
		comments = []
		if verify == True:
			vURL = 'https://movie.douban.com/subject/%s/comments?sort=new_score'%movieId
			vsoup = BeautifulSoup(self.login_session.get(vURL).text,'lxml')
			vcontentdiv = vsoup.find("div", {"id": "content"})
			tag = vcontentdiv.find("span",{"class":"fleft"})
			self.total = int(tag.contents[0].split(u'\u5171')[1].split(u'\u6761')[0])
			logging.warning(
					{datetime.datetime.now():"total comments %d"%self.total}
					)
			if start > self.total - 20:
				raise Exception("not enough comments")
		
		URL = 'https://movie.douban.com/subject/%s/comments?status=P&start=%d&limit=20&sort=new_score'%(movieId,start)
		try:
			page = self.login_session.get(URL, timeout=10)
		except requests.exceptions.ConnectionError:
			logging.warning("requests.exceptions.ConnectionError")
			return "page load error."
		except requests.exceptions.ConnectTimeout:
			logging.warning("ConnectTimeout")
			return "ConnectTimeout"
		except requests.exceptions.ReadTimeout:
			logging.warning("ReadTimeout")
			return "ConnectTimeout"
		soup = BeautifulSoup(page.text,'lxml')
		contentdiv = soup.find("div", {"id": "content"})
		commentsdiv = contentdiv.findAll("div",{"class":"comment-item"})

		logging.warning("find %d comments sesection."%len(commentsdiv))
		for item in commentsdiv:
			comment_data = self.parseComments(item)
			if comment_data == 'no rating found' or comment_data == 'viwer has not seen the move.':
				continue
			else:
				comments.append(comment_data)
		logging.warning("load %d valid comments in this round."%len(comments))
		return comments

	def parseComments(self,html):
		cid = html.attrs['data-cid']
		info = html.find("span",{"class":"comment-info"})
		rating = info.findChildren("span")
		if rating[0].text != u'看过':
			return 'viwer has not seen the move.'
		else:
			rating_allstar = rating[1]['class'][0]
		if "allstar" not in rating_allstar:
			return 'no rating found'
		else:
			try:
				rating = int(re.sub("[^0-9]", "", rating_allstar))
			except:
				rating = -1
			try:
				vote = int(html.find("span",{"class":"comment-vote"}).contents[1].contents[0])
			except:
				vote = -1
			try:
				comment_text = html.find("p").contents[0].replace('\n','').strip()
			except:
				comment_text = ''
			try:	
				date = info.find("span",{"class":"comment-time "}).attrs['title']
			except:
				date = ''
				
			return {"cid":cid,"date":date,"rating":rating,"vote":vote,"comment":comment_text}





