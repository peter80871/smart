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

def get_commands():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM "TEAM_IN_LEAGUES"')
    c = c.fetchall()
    conn.close()
    return c 

def get_html(country, team, howmuch, cookie, token, comp):
    print(f'{team}: {comp}')
    HEADERS ={
        'X-CSRF-TOKEN': f'{token}',
        'Cookie': f'{cookie}'}
    PARAMS = {
        'team': 'home',
        'name': f'{team}',
        'seasons': 'Все',
        'competitions': f'{country}: {comp}',
        'where': 'Все',
        'howmuch': f'{howmuch}',
        'stat': 'Голы',
        'half': 'Первый тайм',
        'lng': 'ru',
        'client': 'free',
        'answer_id': 'teamAnswer',
        'source': 'Основной источник',
        'oddsrange': 'all',
        'situation': 'all',
        'after_int_cup': 'all'}

    response = requests.post('https://smart-tables.ru/show/constructed', headers=HEADERS, params=PARAMS)
    if response.status_code == 200:
        #print(200)
        return response.text
    else:
        print(response.status_code)

def get_actual_matches(team, cookie, token):
    HEADERS ={
        'X-CSRF-TOKEN': f'{token}',
        'Cookie': f'{cookie}'}

    PARAMS = {'name': f'{team}'}

    response = requests.post('https://smart-tables.ru/show/team_fixtures', headers=HEADERS, params=PARAMS)

    if response.status_code == 200:
        #print(200)
        return response.text
    else:
        print(response.status_code)

def add_data(country, league, team, cookie, token):
    data = get_html(country, team, 100, cookie, token, league)
    item_lxml = html.fromstring(data)
    soup = BeautifulSoup(data, 'html.parser') 
    all_mathes = soup.find_all('tr', class_='match-row') 

    q_m = len(all_mathes)
    print(q_m)
    
    team1 = [item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[{x+1}]/td[4]/a/@href')[0][6:] for x in range(q_m)]   # team 1
    team2 = [item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[{x+1}]/td[7]/a/@href')[0][6:] for x in range(q_m)]   # team 2
    t1 = [item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[{x+1}]/td[5]/text()')[0] for x in range(q_m)]           # Счет первой команды
    t2 = [item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[{x+1}]/td[6]/text()')[0] for x in range(q_m)]           # Счет второй команды
    date = [item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[{x+1}]/td[3]/@title')[0] for x in range(q_m)]         # Дата проведения матча
    t = [item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[{x+1}]/td[8]/text()')[0] for x in range(q_m)]
    
    for x in range(q_m): 
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        data = (country, league, team, team1[x], team2[x], t1[x], t2[x], date[x], t[x])   # Вся информация о матче
        c.execute("INSERT INTO ALL_MATCHES VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", data)      # Добавление данных в БД
        conn.commit()
        conn.close()
    print('writed')

def add_data_match(team, cookie, token):
    data = get_actual_matches(team, cookie, token)
    item_lxml = html.fromstring(data)
    soup = BeautifulSoup(data, 'html.parser')  
    all_mathes = soup.find_all('div', class_='inbox-item') 
    
    q_m = len(all_mathes)
    #print(q_m)
    if q_m > 1:
        teams = [item_lxml.xpath(f'div[{x+1}]/p[1]/a/text()')[0].split(' - ') for x in range(q_m)]
        league = [item_lxml.xpath(f'div[{x+1}]/p[2]/a/text()')[0] for x in range(q_m)]
        date = [item_lxml.xpath(f'//div/p/a')[0] for x in range(q_m)]
        _date = [f'{item_lxml.xpath(f"div[{x+1}]/p[3]/text()")[0]}.21' for x in range(q_m)]

        for x in range(q_m):
            item_lxml = html.fromstring(requests.get(f'https://smart-tables.ru/{date[x].get("href")}').text)

            time_match = item_lxml.xpath('/html/body/div[1]/div/div/div[3]/div[2]/div[1]/div/div[1]/div/div[2]/p/text()[2]')[0].split(' ')[1].split('\n')[0]
            
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            data = (league[x], teams[x][0], teams[x][1], _date[x], time_match)   # Вся информация о матче
            c.execute("INSERT INTO UPCOMING_MATCHES VALUES(?, ?, ?, ?, ?);", data)      # Добавление данных в БД
            conn.commit()
            conn.close()
        print('writed')

def r(t, cookie, token, commands):
    db.db_drop('ALL_MATCHES')
    for i in range(0,len(commands)-4, 4):
        #print(commands[i+t])
        try:
            add_data(commands[i+t][0], commands[i+t][1], commands[i+t][2], cookie, token)
        except:
            pass

def r2(t, cookie, token, commands):
    db.db_drop('UPCOMING_MATCHES')
    for i in range(0,len(commands)-4, 4):
        #print(commands[i+t])
        add_data_match(commands[i+t][2], cookie, token)

def multi():
    cookie, token = get_cookie()
    commands = get_commands()
    #for i in range(4):
    #    th = Thread(target=r, args=(i, cookie, token, commands))
    #    th.start()
   
    for i in range(4):
        th = Thread(target=r2, args=(i, cookie, token, commands))
        th.start()

multi()