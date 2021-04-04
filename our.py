import datetime
import db

def today_match():
    d = list(set(db.show_data_in_table('UPCOMING_MATCHES')))
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=3)
    dd = str(tomorrow)
    tomorrow = str(tomorrow).split('-')
    upcoming_matches = [i for i in d if i[3].split('.')[0] == tomorrow[2] and i[3].split('.')[1] == tomorrow[1]]

    return upcoming_matches, dd
        
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
        'coach_option': 'all',
        'after_int_cup': 'all'}

    response = requests.post('https://smart-tables.ru/show/constructed', headers=HEADERS, params=PARAMS)
    if response.status_code == 200:
        print(200)
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
        print(200)
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
    print(q_m)
    if q_m > 1:
        teams = [item_lxml.xpath(f'div[{x+1}]/p[1]/a/text()')[0].split(' - ') for x in range(q_m)]
        league = [item_lxml.xpath(f'div[{x+1}]/p[2]/a/text()')[0] for x in range(q_m)]
        date = [f'{item_lxml.xpath(f"div[{x+1}]/p[3]/text()")[0]}.21' for x in range(q_m)]
        for x in range(q_m):
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            data = (league[x], teams[x][0], teams[x][1], date[x])   # Вся информация о матче
            c.execute("INSERT INTO UPCOMING_MATCHES VALUES(?, ?, ?, ?);", data)      # Добавление данных в БД
            conn.commit()
            conn.close()
        print('writed')

def r(t, cookie, token, commands):
    db.db_drop('ALL_MATCHES')
    for i in range(0,len(commands)-4, 4):
        print(commands[i+t])
        try:
            add_data(commands[i+t][0], commands[i+t][1], commands[i+t][2], cookie, token)
        except:
            print('o')

def r2(t, cookie, token, commands):
    db.db_drop('UPCOMING_MATCHES')
    for i in range(0,len(commands)-4, 4):
        print(commands[i+t])
        add_data_match(commands[i+t][2], cookie, token)

def multi(k):
    cookie, token = get_cookie()
    commands = get_commands()
    if k == 1:
        for i in range(4):
            th = Thread(target=r, args=(i, cookie, token, commands))
            th.start()
    if k == 2:
        for i in range(4):
            th = Thread(target=r2, args=(i, cookie, token, commands))
            th.start()

import requests

def finder(t1, t2):
    t1_matches = requests.get(f'https://m.melbet.ru/LineFeed/Web_SearchZip?text={t1}&limit=150&lng=ru&partner=195&mode=6')
    t2_matches = requests.get(f'https://m.melbet.ru/LineFeed/Web_SearchZip?text={t2}&limit=150&lng=ru&partner=195&mode=6')

    matches1 = t1_matches.json()
    matches2 = t2_matches.json()

    matches1 = matches1['Value']
    matches2 = matches2['Value']
    total_t1_b, total_t1_m, total_t2_b, total_t2_m = '~','~','~','~'
    try:
        for match in matches1:
            for match2 in matches2:
                if match2['CI'] == match['CI']:
                    LI = match['LI']    # leageu code (first arg)
                    CI = match['CI']    # match code
                    LE = match['LE']    # league name
                    O1 = match['O1E']   # first team
                    O2 = match['O2E']   #second team
                  
                    id_t = requests.get(f'https://m.melbet.ru/LineFeed/GetGameZip?id={CI}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&countevents=50&partner=195&grMode=2').json()

                    I = id_t['Value']['SG'][0]['I']

                    l = O1.split()
                    O1 = '-'.join(l)
                    l = O2.split()
                    O2 = '-'.join(l)  
                    
                    LE = LE.split('.')
                    LE = ''.join(LE)
                    l = LE.strip('.').split()
                    LE = '-'.join(l)  

                    #href = f'https://m.melbet.ru/line/Football/{LI}-{LE}/{CI}-{O1}-{O2}'    #https://m.melbet.ru/LineFeed/GetGameZip?id=96230530&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&countevents=50&partner=195&grMode=2
                    
                    rrrr = requests.get(f'https://m.melbet.ru/LineFeed/GetGameZip?id={I}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&countevents=200&partner=195&grMode=2').json()

                    all_params = rrrr['Value']
                    all_totals = all_params['GE']
                    
                    total_t1_b = all_totals[7]['E'][0][0]['C'] 
                    total_t1_m = all_totals[7]['E'][1][0]['C']

                    total_t2_b = all_totals[9]['E'][0][0]['C']
                    total_t2_m = all_totals[9]['E'][1][0]['C']
    except:
        print('no kf')

    return total_t1_b, total_t1_m, total_t2_b, total_t2_m

import requests
import sqlite3
import parser
import line
import schedule, time
import telebot
from multiprocessing.context import Process
import key

def nnn():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    user_id = 410250411
    c.execute(f"INSERT INTO BOT_USERS (user_id) VALUES ({user_id});")
    conn.commit()
    conn.close()

bot = telebot.TeleBot(key.tg)

def get_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM BOT_USERS;')
    users = c.fetchall()
    conn.close()
    return users

def append_data(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    users = get_users()
    if len(users) == 0:
        nnn()

    status = 0
    for i in range(len(users)):
        if user_id == int(users[i][-1]):
            status = 1
    if status == 0:
        c.execute(f"INSERT INTO BOT_USERS (user_id) VALUES ({user_id});")
        conn.commit() 
        conn.close()
        print(status)
        return 1
    else:
        print(status)
        conn.close()
        return 0


def send_message1():
    matches = line.get_message()
    for match in range(len(matches)):
        country, league, team1, team2, date, t, c, kf = matches[match]
        
        msg = f'''Сигнал #{match+1} 🚨\n{country} {league}\n{team1} - {team2}\nНачало матча {date}\nСтавка - ИТ{t}{c}(0,5) в первом тайме\nКоэффициент - {kf}'''
        print(msg)
        for user_id in get_users():
            print(user_id)
            bot.send_message(user_id[0], msg)


schedule.every().day.at("19:16").do(send_message1)
#schedule.every().day.at("9:59").do(parser.multi(1))
#schedule.every().day.at("10:59").do(parser.multi(2))

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    print(user_id)
    if append_data(user_id):
        bot.send_message(message.chat.id, 'Вы подписались на рассылку')
    else:
        bot.send_message(message.chat.id, 'Вы уже есть в базе рассылки') 

class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
 
    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()
 
 
if __name__ == '__main__':
    ScheduleMessage.start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass

import sqlite3 
import data
import today_matches
from datetime import datetime
import time 
import today_matches
import melbet_parser

def get_commands():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM "TEAM_IN_LEAGUES"')
    c = c.fetchmany(100000)

    return c

def get_matches(command, league):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM "ALL_MATCHES" WHERE team = "{command}" AND series = "{league}"')

    return c.fetchmany(10000)

def delete_underline(winner):
    try:
        winner = winner.split('_')
        if len(winner) == 1:
            winner = winner[0]
        elif len(winner) == 2:
            winner = winner[0] + ' ' + winner[1]
        elif len(winner) == 3:
            winner = winner[0] + ' ' + winner[1] + ' ' + winner[2]
        elif len(winner) == 4:
            winner = winner[0] + ' ' + winner[1] + ' ' + winner[2] + ' ' + winner[3]  
    except:
        pass

    return winner

def get_matches_series(matches):
    all_matches_series = []
    a = []
    for match in matches:
        country, league, team, team1, team2, t1, t2, date, t = match
        team1 = delete_underline(team1)
        team2 = delete_underline(team2)
        if t1 == '?':
            t1, t2 = 0, 0
        t1 = int(t1) 
        t2 = int(t2)
            
        if team == team1:
            if t1 >= 1:
                a.append(1)
            else:
                a.append(0)
        elif team == team2:
            if t2 >= 1:
                a.append(1)
            else:
                a.append(0)
    return a

def line_append(line):
    len_win_line = 0
    len_lose_line = 0

    now_win_line = 0
    now_lose_line = 0

    for i in line:
        if i == 1:
            now_win_line += 1
            now_lose_line = 0
            if now_win_line > len_win_line:
                len_win_line = now_win_line

        else:
            now_lose_line += 1
            now_win_line = 0
            if now_lose_line > len_lose_line:
                len_lose_line = now_lose_line

    return len_lose_line, len_win_line

def line_analizer(line):
    len_lose_line, len_win_line = line_append(line)
    b = 0
    c = 0

    if len_lose_line > len_win_line:
        len_lose_line_after, len_win_line_after = line_append(line[len_lose_line:])
        
    else:
        len_lose_line_after, len_win_line_after = line_append(line[len_win_line:])
        


    if len_lose_line >= len_lose_line_after+2:
        b = line[:len_lose_line].count(0)

    if len_win_line >= len_win_line_after+2:
        c = line[:len_win_line].count(1)   

    a = [len_lose_line, len_lose_line_after, len_win_line, len_win_line_after, b, c]
    
    return a

def get_line(team, league):
    m = get_matches(team, league)
    m_sorted = []

    for i in range(len(m)):
        m_sorted.append(m[i])
    return get_matches_series(m_sorted)

def get_message():

    m_today = today_matches.today_match()[0]

    msg = []
    for m in m_today:
        if m[0][-3:] != 'Cup':
            for command in get_commands():
                if command[2] == m[1]:
                    if len(get_line(command[2], command[1])) > 5:
                        n = line_analizer(get_line(command[2], command[1]))
                        if n[4] == n[0] or n[5] == n[2]:
                            kfs = melbet_parser.finder(m[1],m[2])
                            t = 1
                            if n[0] > n[2]:
                                c = 'Б'
                                kf = kfs[0]
                            else:
                                c = 'М'
                                kf = kfs[1]

                            
                            msg.append([command[0], command[1], m[1], m[2], m[3], t, c, kf])
                            


                elif command[2] == m[2]:
                    if len(get_line(command[2], command[1])) > 5:
                        n = line_analizer(get_line(command[2], command[1]))
                        if n[4] == n[0] or n[5] == n[2]:
                            kfs = melbet_parser.finder(m[1],m[2])
                            t = 2
                            if n[0] > n[2]:
                                c = 'Б'
                                kf = kfs[2]
                            else:
                                c = 'М'
                                kf = kfs[3]


                            msg.append([command[0], command[1],  m[1], m[2], m[3], t, c, kf])
    return msg

print(get_message())

import sqlite3


def db_create():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    #c.execute('CREATE TABLE "TEAM_IN_LEAGUES" (country TEXT, league TEXT, team TEXT);')
    c.execute('CREATE TABLE "ALL_MATCHES" (league TEXT, series TEXT, team TEXT, team1 TEXT, team2 TEXT, t1 INTEGER, t2 INTEGER, date TEXT, t INTEGER);')
    c.execute('CREATE TABLE "UPCOMING_MATCHES" (league TEXT, team1 TEXT, team2 TEXT,  date TEXT);')
    c.execute('CREATE TABLE "BOT_USERS" (user_id INT);')
    conn.commit()
    conn.close()


def db_drop(table):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(f"DROP TABLE {table};")

    if table == "UPCOMING_MATCHES":
        c.execute(
            'CREATE TABLE "UPCOMING_MATCHES" (league TEXT, team1 TEXT, team2 TEXT,  date TEXT);'
        )

    elif table == "ALL_MATCHES":
        c.execute(
            'CREATE TABLE "ALL_MATCHES" (league TEXT, series TEXT, team TEXT, team1 TEXT, team2 TEXT, t1 INTEGER, t2 INTEGER, date TEXT, t INTEGER);'
        )
    # c.execute('CREATE TABLE "BOT_USERS" (user_id INT);')
    # c.execute('CREATE TABLE "ALL_MATCHES" (league TEXT, series TEXT, team TEXT, team1 TEXT, team2 TEXT, t1 INTEGER, t2 INTEGER, date TEXT, t INTEGER);')

    conn.commit()
    conn.close()


def show_tables():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        """select * from sqlite_master
            where type = 'table'"""
    )
    tables = c.fetchall()
    conn.close()

    return tables


def show_data_in_table(table):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(f'SELECT * FROM "{table}"')

    c = c.fetchmany(2000)
    conn.close()

    return c