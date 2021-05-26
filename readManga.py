import requests
from bs4 import BeautifulSoup
import fake_useragent
import csv
import json
import os.path
import os
import sqlite3
import threading
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
    DOMAINS = ['http://readmanga.live', "https://mintmanga.live"]
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
            title = item.find('a', class_='site-element').nextSibling.attrs['data-title']
            linkComponent = item.find('a',class_='go-to-chapter')
            chapterLink = linkComponent.attrs['href']
            genChapters = linkComponent.text.split('-')
            bLink = item.find('a', class_='site-element').attrs['href']
            volume = genChapters[0]
            chapter = genChapters[1]


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
    		return content


    	else:
    		print('Error')
    		return ''

    def get_content(self,html):
        soup = BeautifulSoup(html,'html.parser')
        item = soup.find('h4')
        title = soup.find('span', class_='name').text
        chapter_link = soup.find('a', class_='chapter-link btn btn-outline-primary btn-lg btn-block read-first-chapter').attrs['href']
        if(item and item.find('a')):
            linkComponent = item.find('a',class_='go-to-chapter')
            genChapters = item.find('a').text.replace('Читать ','').replace(' новое', '')
            genChapters = genChapters.split(' - ') if genChapters.find('-') != -1 else genChapters.split(' ')
            volume = genChapters[0]
            chapter = genChapters[1]


        else:
            dom = ""
            for domain in self.DOMAINS:
                html = self.get_html(domain+chapter_link)
                if(html.status_code == 200):
                    dom = domain
                    break
            
            volume, chapter = self.get_chapter_directly(self.get_html(dom + chapter_link).text)

        return {
                'title':title,
                'volume': volume,
                'chapter':chapter
            }

            


    def get_chapter_directly(self,html):
        soup = BeautifulSoup(html,'html.parser')
        last_chapter = soup.find('option').text.split(' - ')
        return last_chapter[0], last_chapter[1]

    def get_fresh_books(self):
        links = [book['link'] for book in self.books]
        
        with Pool(int(len(links)/5)) as p:
            self.fresh_books = p.map(self.parse,links)
        



        return self.fresh_books


    def check_unreads(self):
        self.unreads.clear()
        self.fresh_books = self.get_fresh_books()
        is_done = False
        """
        for book in self.books:
            if book['title'] != None and book['volume'] != None and book['chapter'] != None:
                for fresh_book in self.fresh_books:
                    if book['title'] == fresh_book['title']:
                        if(book['volume'] != fresh_book['volume'] or book['chapter'] != fresh_book['chapter']):
                            self.unreads.append("<a href = '%s'> %s :: %s volume %s chapter => %s volume %s chapter </a>"%(book['cLink'],book['title'],book['volume'],book['chapter'],
                                fresh_book['volume'],fresh_book['chapter']))
                            break
        """
        self.unreads = ["<a href = '%s'> %s :: %s volume %s chapter => %s volume %s chapter </a>"%(book['cLink'], book['title'],
                        book['volume'], book['chapter'], fresh_book['volume'], fresh_book['chapter'])
                        for book in self.books
                            if book['title'] != None and book['volume'] != None and book['chapter'] != None
                        for fresh_book in self.fresh_books
                            if book['title'] == fresh_book['title'] and
                        (book['volume'] != fresh_book['volume'] or book['chapter'] != fresh_book['chapter'])]


    def refresh_books(self):
        self.fresh_books = [fresh_book for fresh_book in fresh_books if 'link' in fresh_book]




def main():

    parser = Parser(335271283,'1.db')

	#USER_DATA = get_user_data(user_id,db_path


    parser.parse_bookmarks()
    parser.check_unreads()

    for unread in parser.unreads:
        print(unread + '\n')




if __name__ == '__main__':
    main()
