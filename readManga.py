import requests
from bs4 import BeautifulSoup
import fake_useragent
import csv
import json
import os.path
import os
import sqlite3
from datetime import datetime
#from threading import Thread
#import time
from multiprocessing import Pool












class Parser:
    LINK = "https://grouple.co/login/authenticate?tt"

    session = requests.Session()

    BOOKMARKS_URL = "https://grouple.co/private/bookmarks"

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.107'

    HEADER = {
    	'user-agent' : USER_AGENT
    }
    USER_DATA = {}
    books = []

    fresh_books = []

    unreads = []

    username = ''
    password = ''

    r_num = 0

    def __init__(self,user_id,db_file):
        self.user_id = user_id
        self.db_file = db_file
        self.USER_DATA = self.get_user_data()
        self.session.post(self.LINK,data = self.USER_DATA)

    def get_user_data(self):
    	db = sqlite3.connect(self.db_file)
    	cursor = db.cursor()
    	isExist = cursor.execute(f"SELECT * FROM subscriptions WHERE user_id = ? ",(self.user_id,)).fetchall()

    	if(isExist):
    		self.username = cursor.execute(f"SELECT username FROM subscriptions WHERE user_id = ?",(self.user_id,)).fetchone()[0]
    		self.password = cursor.execute(f"SELECT password FROM subscriptions WHERE user_id = ?",(self.user_id,)).fetchone()[0]
    		return {'username':self.username,'password':self.password}
    	else:
    		return {}

    def get_html(self,url, params=None):
    	r = self.session.get(url,headers=self.HEADER,params=params)
    	return r


    def get_bookmarks_content(self,html):
        soup = BeautifulSoup(html,'html.parser')
        items = soup.find_all('tr' , class_= 'bookmark-row')
        for item in items:
            title = item.find('a',class_='site-element').nextSibling.attrs['data-title']
            linkComponent = item.find('a',class_='go-to-chapter')
            chapterLink = linkComponent.attrs['href']
            genChapters = linkComponent.text.replace('-',' ')
            genChapters = list(genChapters)
            bLink = item.find('a',class_='site-element').attrs['href']
            volume = genChapters[0]
            chapter = ''.join(genChapters[2:len(genChapters)]).replace(' ', '')


            self.books.append({
                'title': title,
                'volume':volume,
                'chapter':chapter,
                'link': bLink,
                'cLink':chapterLink

            })

        return self.books


    def parse_bookmarks(self):
    	html = self.get_html(self.BOOKMARKS_URL)
    	if(html.status_code == 200):
            self.books = self.get_bookmarks_content(html.text)
    	else:
    		print('Error')

    def parse(self,url):
    	html = self.get_html(url)
    	if(html.status_code == 200):
    		content = self.get_content(html.text)
    		#fresh_books.append(content)
    		return content


    	else:
    		print('Error')
    		return ''

    def get_content(self,html):
    	"""
    		Obtain title, volume and chapter from HTML.

    		HTML should be connected to grouple.co
    	"""
    	soup = BeautifulSoup(html,'html.parser')
    	item = soup.find('h4')
    	title = soup.find('span', class_='name').text
    	if(item and item.find('a')):
    		genChapters = item.find('a').text.replace('Читать ','')
    		genChapters = genChapters.replace('-','')
    		genChapters = genChapters.replace(' новое', '')
    		genChapters = list(genChapters)
    		volume = genChapters[0]
    		chapter = ''.join(genChapters[2:len(genChapters)]).replace(' ','')
    		#print(title)

    		return {
    			'title':title,
    			'volume':volume,
    			'chapter':chapter
    		}
    	else:
    		return {
    			'title':title,
    			'volume': None,
    			'chapter': None
    		}

    def get_fresh_books(self):
        links = [book['link'] for book in self.books]
        """
        for book in self.books:
            links.append(book['link'])
        """
        with Pool(10) as p:
            self.fresh_books = p.map(self.parse,links)

        return self.fresh_books


    def check_unreads(self):
        self.unreads.clear()
        self.fresh_books = self.get_fresh_books()
        """for book in self.books:
        	for fresh_book in self.fresh_books:
        		if book['title'] == fresh_book['title']:
        			if(book['volume'] != fresh_book['volume'] or book['chapter'] != fresh_book['chapter']):
        				fresh_book['link'] = book['cLink']
        					#print(fresh_book['cLink'])
        				self.unreads.append("<a href = '%s'> %s :: %s volume %s chapter => %s volume %s chapter </a>"%(fresh_book['link'],book['title'],book['volume'],book['chapter'],
        				fresh_book['volume'],fresh_book['chapter']))
        """
        self.unreads = ["<a href = '%s'> %s :: %s volume %s chapter => %s volume %s chapter </a>"%(book['cLink'],
                        book['title'], book['volume'], book['chapter'],
                        fresh_book['volume'], fresh_book['chapter']) 
                        for book in self.books 
                        for fresh_book in self.fresh_books 
                        if book['title'] == fresh_book['title'] and 
                        (book['volume'] != fresh_book['volume'] or book['chapter'] != fresh_book['chapter'])]

        #print(self.unreads)
        #self.refresh_books()

    def refresh_books(self):
        new_fresh_books = [fresh_book for fresh_book in fresh_books if 'link' in fresh_book]
        """for fresh_book in self.fresh_books:
            if 'link' in fresh_book:
                new_fresh_books.append(fresh_book)"""
        self.fresh_books.clear()
        self.fresh_books = new_fresh_books.copy()




def main():

    parser = Parser(335271283,'1.db')

	#USER_DATA = get_user_data(user_id,db_path


    parser.parse_bookmarks()
    parser.check_unreads()

    for unread in parser.unreads:
        print(unread + '\n')




if __name__ == '__main__':
    main()
