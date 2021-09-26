import requests
from bs4 import BeautifulSoup
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
    LINK = "https://grouple.co/login/authenticate?ttt"

    session = requests.Session()

    BOOKMARKS_URL = "https://grouple.co/private/bookmarks"
    AUTH_URL = "https://grouple.co/internal/auth/login"

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'

    HEADER = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    }

    USER_DATA = {}

    DOMAINS = ['https://readmanga.io', "https://mintmanga.live"]

    books = []

    fresh_books = []

    unreads = []

    username = ''
    password = ''

    r_num = 0

    def __init__(self,user_id,db_file):
        """
            Инициализация
        """
        self.user_id = user_id
        self.db_file = db_file
        self.USER_DATA = self.get_user_data()
        self.USER_DATA
        self.session.post(self.LINK,data = self.USER_DATA, headers=self.HEADER)
        #self.set_cookies()

    def print_cookies(self):
        print('='.join(self.session.cookies.items()[0]))

    def set_cookies(self):
        self.HEADER['Cookie'] = '='.join(self.session.cookies.items()[0])



    def get_user_data(self):
        """
            Функция получает данных с базы данных и их возвращение
        """
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
        """
            Функция отправляет GET запрос на заданный URL,
            получает ответ и возвращает его
        """
        r = self.session.get(url, headers = self.HEADER)
        return r


    def get_bookmarks_content(self,html):
        """Функция получает со страницы закладок:
            - Название
            - Том
            - Главу
            - Ссылку на произведение
            - Ссылку на главу
        А также возвращает полученную информацию в виде списка с вложенными словарями

        """
        soup = BeautifulSoup(html,'html.parser')
        items = soup.find_all('tr' , class_= "bookmark-row")
        for item in items:
            link_container = item.find('a', class_="site-element")
            title = link_container.nextSibling.attrs['data-title']
            linkComponent = item.find('a',class_='go-to-chapter')
            chapterLink = linkComponent.attrs['href']
            genChapters = linkComponent.text.split('-')
            bLink = item.find('a', class_='site-element').attrs['href']
            volume = genChapters[0].replace(" ", '')
            chapter = genChapters[1].replace(" ", '')


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
            print('Error: Can not get bookmarks')

    def parse(self,url):
    	html = self.get_html(url)
    	if(html.status_code == 200):
            content = self.get_content(html.text)
            return content


    	else:
            print('Error: ' + str(html.status_code))
            return ''

    def get_content(self,html):
        soup = BeautifulSoup(html,'html.parser')
        item = soup.find('h4')
        title = soup.find('span', class_='name').text
        rm_first_chapter_class = 'chapter-link btn btn-outline-primary btn-lg btn-block read-first-chapter'
        mm_first_chapter_class = rm_first_chapter_class + " manga-mtr"
        chapter_block = soup.find('a', class_=rm_first_chapter_class)
        try:
            chapter_link = soup.find('a', class_=rm_first_chapter_class).attrs['href'] if chapter_block != None else soup.find('a', class_=mm_first_chapter_class).attrs['href']
        except AttributeError:
            return {
                'title':title,
                'volume': "No info",
                'chapter': "No info"
            }

        if(item and item.find('a')):
            linkComponent = item.find('a',class_='go-to-chapter')
            genChapters = item.find('a').text.replace('Читать ','').replace(' новое', '')
            genChapters = genChapters.split(' - ') if genChapters.find('-') != -1 else genChapters.split(' ')
            volume = genChapters[0]
            chapter = genChapters[1]


        else: #Случай когда блок с ссылкой отсутсвует
            dom = ""
            for domain in self.DOMAINS:
                html = self.get_html(domain+chapter_link)
                if(html.status_code == 200):
                    dom = domain
                    break
            
            volume, chapter = self.get_chapter_directly(self.get_html(dom + chapter_link).text)

        return {
                'title':title,
                'volume': volume.replace(" ", ''),
                'chapter':chapter.replace(" ", '')
            }

            


    def get_chapter_directly(self,html):
        soup = BeautifulSoup(html,'html.parser')
        last_chapter = soup.find('option').text.split(' - ')
        return last_chapter[0], last_chapter[1]


    def get_fresh_books(self):
        links = [book['link'] for book in self.books]
        
        try:
            with Pool(int(len(links)/5)) as p:
                self.fresh_books = p.map(self.parse, links)
        except ValueError:
            print("Error: Books list is empty")
            self.fresh_books = []
        

        return self.fresh_books

    def get_html_bookmarks(self):
        bookmarks = []
        if len(self.books) < 1:
            self.parse_bookmarks() 
        else:
            return []
        bookmarks = ['<a href = "%s"> %s </a>'%(book['cLink'],book['title']) + '\n' for book in self.books]
        return bookmarks



    def get_html_unread(self, cLink, title, volume, chapter, f_volume,f_chapter):
        return "<a href = '%s'> %s :: %s volume %s chapter => %s volume %s chapter </a>"%(cLink, title, volume, chapter, f_volume,f_chapter)


    def check_unreads(self):
        if len(self.books) < 1:
            self.parse_bookmarks()
        self.unreads.clear()
        self.fresh_books = self.get_fresh_books()
        
        for book in self.books:
            for fresh_book in self.fresh_books:
                if book['title'] == fresh_book['title'] and ((book['volume']+book['chapter']) != (fresh_book['volume']+fresh_book['chapter'])):
                    self.unreads.append(self.get_html_unread(book['cLink'],book['title'],book['volume'],book['chapter'],fresh_book['volume'],fresh_book['chapter']))
                    break


    def refresh_books(self):
        self.fresh_books = [fresh_book for fresh_book in fresh_books if 'link' in fresh_book]




def main():

    parser = Parser(335271283,'1.db')

	#USER_DATA = get_user_data(user_id,db_path
    parser.check_unreads()

    """for unread in parser.unreads:
        print(unread + '\n')"""




if __name__ == '__main__':
    main()
