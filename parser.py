import requests
from bs4 import BeautifulSoup
import fake_useragent
import csv
import json
import os.path
import os
from datetime import datetime
#from threading import Thread
#import time
from multiprocessing import Pool



#Variables and constants
LINK = "https://grouple.co/login/authenticate?tt"

session = requests.Session()



USER_PATH = 'login_data.json'

BOOKMARKS_URL = "https://grouple.co/private/bookmarks"

FILE_CSV = 'bookList.csv'

FILE_JSON = 'bookList.json'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.107'

HEADER = {
	'user-agent' : USER_AGENT
}

UNREADS_PATH = 'unreads.txt'

books = []

fresh_books = []

unreads = []


def get_user_data(path, data):
	"""
		Function that gets username and password of user and insert them into dictionary

		path - path to the login data FILE_CSV

		data - container of obtained data
	"""
	if(os.path.isfile(path)):
		with open(path, 'r') as file:
			data = json.load(file)
		if(len(data) == 0 or (data['username'] == '' or data['password'] == '')):
			username = str(input('Введите логин:'))
			password = str(input('Введите пароль:'))

			data = {
				'username': username,
				'password': password
			}

			with open(path,'w+') as file:
				json.dump(data,file,indent=3)
	else:
		with open(data,'w+') as file:
			json.dump({},file,indent=3)
	return data



def save_csv_file(items,path):
	with open(path,'w',newline='') as file:
		writer = csv.writer(file,delimiter=';')
		writer.writerow(['Название','Том','Глава','Ссылка'])
		for item in items:
			writer.writerow([item['title'],item['volume'],item['chapter'],item['link']])


def save_json_file(items,path):
	with open(path,'w+') as file:
		json.dump(items,file,indent=3)


def get_html(url, params=None):
	r = session.get(url,headers=HEADER,params=params)
	return r



def parse_bookmarks():
	html = get_html(BOOKMARKS_URL)
	if(html.status_code == 200):
		books = get_bookmarks_content(html.text)
		#
	else:
		print('Error')
	save_files()



def parse(url):
	html = get_html(url)
	if(html.status_code == 200):
		content = get_content(html.text)
		#fresh_books.append(content)
		return content


	else:
		print('Error')
		return ''



def get_content(html):
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
			'chapter':chapter,
		}
	else:
		return {
			'title':title,
			'volume': None,
			'chapter': None,
		}









def get_bookmarks_content(html):
	"""
		Recieve title, volume, chapter and link from user's bookmarks.

		HTML should be connected to grouple.co
	"""
	soup = BeautifulSoup(html,'html.parser')
	items = soup.find_all('tr' , class_= 'bookmark-row')

	for item in items:
		title = item.find('a',class_='site-element').nextSibling.attrs['data-title']
		genChapters = item.find('a',class_='go-to-chapter').text.replace('-',' ')
		genChapters = list(genChapters)
		bLink = item.find('a',class_='site-element').attrs['href']
		volume = genChapters[0]
		chapter = ''.join(genChapters[2:len(genChapters)]).replace(' ', '')



		books.append({
			'title': title,
			'volume':volume,
			'chapter':chapter,
			'link': bLink

		})

	return books




def save_unreads(items,path):
	with open(path,'w') as file:
		date = datetime.now().strftime('$d/$m/$y')
		file.write(date)
		file.write('\n')
		file.write('\n')
		for item in items:
			file.write(item)
			file.write('\n')



def load_unreads(path):
	with open(path) as file:
		for line in file:
			line.strip()
			unreads.append(line.replace('\n',''))



def save_files():
	save_csv_file(books,FILE_CSV)
	save_json_file(books, FILE_JSON)


def get_fresh_books():
	#cnt = 1
	links = []
	for book in books:
		links.append(book['link'])
		#print('Parsing ' + str(cnt) + ' page')
		#parse(book['link'])
		#th = Thread(target = parse, args = (book['link'], ))
		#th.start()
		#cnt+=1
	#print(links)
	with Pool(10) as p:
		fresh_books = p.map(parse,links)
	return fresh_books




def check_unreads():
	unreads.clear()
	fresh_books = get_fresh_books()
	for book in books:
		for fresh_book in fresh_books:
			if book['title'] == fresh_book['title']:
				if(book['volume'] != fresh_book['volume'] or book['chapter'] != fresh_book['chapter']):
					unreads.append("%s :: %s volume %s chapter => %s volume %s chapter" %(book['title'],book['volume'],book['chapter'],
					fresh_book['volume'],fresh_book['chapter']))
	save_unreads(unreads, UNREADS_PATH)
	#print(unreads)


def show_unreads():
	for unread in unreads:
		print(unread + '\n')



def main():
	USER_DATA = {}
	USER_DATA = get_user_data(USER_PATH, USER_DATA)
	response = session.post(LINK,data = USER_DATA)

	parse_bookmarks()

	#th1 = Thread(target = parse_bookmarks)
	#th1.start()
	#load_unreads(UNREADS_PATH)


	check_unreads()

	#th2 = Thread(target = check_unreads)
	#th2.start()

	#th1.join()
	#th2.join()
	show_unreads()








if __name__ == "__main__":
	main()
