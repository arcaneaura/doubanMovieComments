# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib2 import urlopen
import requests
import logging
logging.getLogger().setLevel(logging.DEBUG)
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
		login_data = {'form_email':self.user, 
		              'form_password':self.pw,
		              'captcha-solution': self.captcha_solution,
		              'captcha-id': self.captcha_id,
		              'remember':True}
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
			vsoup = BeautifulSoup(self.login_session.get(vURL),'lxml')
			vcontentdiv = vsoup.find("div", {"id": "content"})
			tag = vcontentdiv.find("span",{"class":"fleft"})
			self.total = int(tag.contents[0].split(u'\u5171')[1].split(u'\u6761')[0])
			logging.warning(
					{datetime.datetime.now():"total comments %d"%self.total}
					)
			if start > self.total - 20:
				raise Exception("not enough comments")
		
		URL = 'https://movie.douban.com/subject/%s/comments?start=%d&limit=20&sort=new_score'%(movieId,start)
		soup = BeautifulSoup(self.login_session.get(URL),'lxml')
		contentdiv = soup.find("div", {"id": "content"})	
		commentsdiv = contentdiv.findAll("div",{"class":"comment-item"})
		
		for item in commentsdiv:
			comments.append(parseComments(self,item))

	def parseComments(self,html):
		cid = html.attrs['data-cid']
		vote = int(
			html.find("span",{"class":"comment-vote"}).contents[1].contents[0]
			)
		


