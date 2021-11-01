import requests
import csv
import json
import os.path
import os
import sqlite3
import threading
import multiprocessing
import asyncio
import aiohttp

from user_requests import User_SQLighter
from bs4 import BeautifulSoup
from datetime import datetime
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

    books = {}

    fresh_books = {}

    unreads = []

    username = ''
    password = ''

    r_num = 0

    def __init__(self, user_id, db):
        """
            Инициализация
        """
        self.user_id = user_id
        self.db = db
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
        isExist = self.db.user_exists(self.user_id)

        if(isExist):
            self.username = self.db.get_username(self.user_id)
            self.password = self.db.get_password(self.user_id)
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



    def get_bs_item_content(self, item):
        link_container = item.find('a', class_="site-element")
        title = link_container.nextSibling.attrs['data-title']
        linkComponent = item.find('a',class_='go-to-chapter')
        chapterLink = linkComponent.attrs['href']
        genChapters = linkComponent.text.split('-')
        bLink = item.find('a', class_='site-element').attrs['href']
        volume = genChapters[0].replace(" ", '')
        chapter = genChapters[1].replace(" ", '')
        return {
                'title': title,
                'volume':volume,
                'chapter':chapter,
                'link': bLink,
                'cLink':chapterLink
                }


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
        self.books = {self.get_bs_item_content(item)['title']:self.get_bs_item_content(item) for item in items}


    def parse_bookmarks(self):
        html = self.get_html(self.BOOKMARKS_URL)
        if(html.status_code == 200):
            self.get_bookmarks_content(html.text)
        else:
            print('Error: Can not get bookmarks')



    async def a_get_html(self, url):
        async with aiohttp.ClientSession() as session:
            r = await session.get(url=url, headers = self.HEADER)
            return await r.text(), r.status


    async def parse(self, url):
        response_text, status_code = await self.a_get_html(url)
        if status_code == 200:
            content = self.get_content(response_text)
            self.fresh_books[content['title']] = content
        else:
            print("Error. Can not get page")

    def get_chapter_info_from_bs_item(self, item):
        linkComponent = item.find('a',class_='go-to-chapter')
        genChapters = item.find('a').text.replace('Читать ','').replace(' новое', '')
        genChapters = genChapters.split(' - ') if genChapters.find('-') != -1 else genChapters.split(' ')
        return genChapters[0], genChapters[1]

    def get_true_domain(self, chapter_link):
        for domain in self.DOMAINS:
            html = self.get_html(domain+chapter_link)
            if(html.status_code == 200):
                return domain
        return -1

    def get_content(self, html):
        soup = BeautifulSoup(html,'html.parser')
        item = soup.find('h4')
        title = soup.find('span', class_='name').text
        rm_first_chapter_class = 'chapter-link btn btn-outline-primary btn-lg btn-block read-first-chapter'
        mm_first_chapter_class = rm_first_chapter_class + " manga-mtr"
        chapter_block = soup.find('a', class_=rm_first_chapter_class)
        try:
            chapter_link = (soup.find('a', class_=rm_first_chapter_class).attrs['href']
                            if chapter_block != None 
                            else soup.find('a', class_=mm_first_chapter_class).attrs['href'])
        except AttributeError:
            return {
                'title':title,
                'volume': "No info",
                'chapter': "No info"
            }
        if(item and item.find('a')):
            volume, chapter = self.get_chapter_info_from_bs_item(item)
        else:
            dom = self.get_true_domain(chapter_link) 
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


    async def get_fresh_books(self):
        links = tuple([book['link'] for _, book in self.books.items()])
        tasks = []
        for link in links:
            task = asyncio.create_task(self.parse(link))
            tasks.append(task)
        await asyncio.gather(*tasks)

    def get_html_bookmarks(self):
        bookmarks = []
        if len(self.books) < 1:
            self.parse_bookmarks() 
        else:
            return []
        bookmarks = tuple(['<a href = "%s"> %s </a>'%(book['cLink'],book['title']) + '\n' for book in list(self.books.items())])
        return bookmarks



    def get_html_unread(self, cLink, title, volume, chapter, f_volume,f_chapter):
        return "<a href = '%s'> %s :: %s volume %s chapter => %s volume %s chapter </a>"%(cLink, title, volume, chapter, f_volume,f_chapter)


    async def check_unreads(self):
        if len(self.books) < 1:
            self.parse_bookmarks()
        self.unreads.clear()
        await self.get_fresh_books()
        self.unreads = [self.get_html_unread(
                            self.books[fresh_book['title']]['cLink'],
                            self.books[fresh_book['title']]['title'],
                            self.books[fresh_book['title']]['volume'],
                            self.books[fresh_book['title']]['chapter'],
                            fresh_book['volume'],
                            fresh_book['chapter']
                            ) for _, fresh_book in self.fresh_books.items() if (self.books[fresh_book['title']]['volume']
                                +self.books[fresh_book['title']]['chapter']) != (fresh_book['volume']+fresh_book['chapter'])]
        """
        for _, fresh_book in self.fresh_books.items():
            title = fresh_book['title']
            book = self.books[fresh_book['title']]
            if (book['volume']+book['chapter']) != (fresh_book['volume']+fresh_book['chapter']):
                self.unreads.append(
                    self.get_html_unread(
                        book['cLink'],
                        book['title'],
                        book['volume'],
                        book['chapter'],
                        fresh_book['volume'],
                        fresh_book['chapter']
                        )
                    )"""




def main():
    db_link = os.getenv('JAWSDB_URL')
    db = User_SQLighter(db_link)

    parser = Parser(335271283, db)
    asyncio.run(parser.check_unreads())

    for unread in parser.unreads:
        print(unread + '\n')




if __name__ == '__main__':
    main()
