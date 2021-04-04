import sqlite3 
import data
import today_matches
from datetime import datetime
import time 
import today_matches
import melbet_parser
from lxml import html
from today_matches import today_match

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

def get_message(day):

    m_today = today_matches.today_match(day)[0]

    msg = []
    for m in m_today:
        if m[0][-3:] != 'Cup':
            for command in get_commands():
                if command[2] == m[1]:
                    if f'{command[0]} {command[1]}' == m[0]:
                        if len(get_line(command[2], command[1])) > 5:
                            n = line_analizer(get_line(command[2], command[1]))
                            if n[4] == n[0] or n[5] == n[2]:
                                kfs = melbet_parser.finder(m[1],m[2])
                                t = '1'
                                if n[0] > n[2]:
                                    c = 'Б'
                                    kf = kfs[0]
                                else:
                                    c = 'М'
                                    kf = kfs[1]
                                if kf > 1.79:
                                    msg.append([command[0], command[1], m[1], m[2], m[3], m[4], t, c, str(kf)])

                elif command[2] == m[2]:
                    if f'{command[0]} {command[1]}' == m[0]:
                        if len(get_line(command[2], command[1])) > 5:
                            n = line_analizer(get_line(command[2], command[1]))
                            if n[4] == n[0] or n[5] == n[2]:
                                kfs = melbet_parser.finder(m[1],m[2])
                                t = '2'
                                if n[0] > n[2]:
                                    c = 'Б'
                                    kf = kfs[2]
                                else:
                                    c = 'М'
                                    kf = kfs[3]
                                if kf > 1.79:
                                    msg.append([command[0], command[1],  m[1], m[2], m[3], m[4], t, c, str(kf)])

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    all_m = c.execute(f'SELECT * FROM PREDICTED_MATCHES').fetchall()

    for i in msg:
        for t in all_m:
            if i[2] == t[2] and i[3] == t[3] and i[4] == t[4]:
                print('exist')
            else:
                c.execute("INSERT INTO PREDICTED_MATCHES VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", i)      # Добавление данных в БД
        conn.commit()
    conn.close()

    return msg

for i in get_message(1):
    print(i)
#def get_message2():
#    print(today_match(0))
        
        #print(get_html(i[0], i[i[5]+1], 1, cookie, token, i[1]))
        #item_lxml = html.fromstring(get_html(i[0], i[i[5]+1], 1, cookie, token, i[1]))

        
        
        #team1 = item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[1]/td[4]/a/@href')[0]   # team 1
        #team2 = item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[1]/td[7]/a/@href')[0]   # team 2
        #t1 = item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[1]/td[5]/text()')[0]          # Счет первой команды
        #t2 = item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[1]/td[6]/text()')[0]           # Счет второй команды
        #date = item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[1]/td[3]/@title')[0]        # Дата проведения матча
        #t = item_lxml.xpath(f'//*[@id="table-home"]/tbody/tr[1]/td[8]/text()')[0]


        #print(t1, t2)
'''
for command in get_commands():
    if len(get_line(command[2], command[1])) > 5:
        n = line_analizer(get_line(command[2], command[1]))
        if n[4] == n[0] or n[5] == n[2]:
            if n[0] > n[2]:
                c = 'Б'
            else:
                c = 'М'

            print(command, n, c)'''