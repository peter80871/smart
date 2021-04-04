import requests
from bs4 import BeautifulSoup
from lxml import html
import sqlite3
from threading import Thread
import time
import db

def get_cookie():
    response = requests.get('https://smart-tables.ru')   # start new session and generate xsrf token

    xsrf = response.headers['Set-Cookie'].split(';')[0]                  # get xsrf token from header
    laravel = response.headers['Set-Cookie'].split(',')[2].split(';')[0] # get laravel token
    soup = BeautifulSoup(response.text, 'html.parser')                   # make soup obj
    user_xsrf = soup.find_all(('meta', 'csrf-token'))[3]['content']      # get user token

    return f'{xsrf};{laravel}', user_xsrf

def get_actual_matches(date, cookie, token):
    HEADERS ={
        'POST': '/show/upcoming HTTP/1.1',
        'Host': 'smart-tables.ru',
        'Connection': 'keep-alive',
        'Content-Length': '55',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'Accept': 'text/plain, */*; q=0.01',
        'X-CSRF-TOKEN': f'{token}',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://smart-tables.ru',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://smart-tables.ru/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Cookie': f'{cookie}'}

    PARAMS = {'date': '2021-03-16'}
    
    response = requests.post('https://smart-tables.ru/show/upcoming', headers=HEADERS, params=PARAMS)

    
    return response.text
   

cookie, token = get_cookie()

print(get_actual_matches('2021-03-16',cookie,token))