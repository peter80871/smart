import requests
import sqlite3
import parser
import line
import schedule, time
import telebot
from multiprocessing.context import Process
import key

bot = telebot.TeleBot(key.tg)


def send_message1():
    matches = line.get_message(0)
    for match in range(len(matches)):
        country, league, team1, team2, time_match, date, t, c, kf = matches[match]
        
        msg = f'''Сигнал #{match+1} 🚨\n{country} {league}\n{team1} - {team2}\nНачало матча {date}\nСтавка - ИТ{t}{c}(0,5) в первом тайме\nКоэффициент - {kf}'''
        print(msg)
        bot.send_message('-1001329764588', msg)
        time.sleep(1000)

def send_message2():
    # [['Colombia', 'Primera A', 'Deportivo Cali', 'Deportivo Pasto', '30.03.21', '0', '1', 'Б', '1.86']]
    #matches = line.get_message(0)
    #for match in range(len(matches)):
    #    country, league, team1, team2, date, t, c, kf = matches[match]
    #['Colombia', 'Primera A', 'Independiente Santa Fe', 'Deportivo Pereira', '03.04.21', '03:40', '1', 'М', '2.19']
    #msgs = f'''Сигнал #1 🚨\nColumbia Primera A\nIndependiente Santa Fe - Deportivo Pereira \nНачало матча 03:40\nСтавка - ИТ1М(0,5) в первом тайме\nКоэффициент - 2.19'''

    msg = '''02.04.2021\nРезультаты матчей 👇\nСигнал #1 , коэффициент 2.65 ❌\nСигнал #2 , коэффициент 2.06 ❌\nСигнал #2 , коэффициент 2.75 ❌\nИтого -3.0% (при флете 1% на ставку)'''

    print(msg)
    bot.send_message('-1001270017440', msg)
        #time.sleep(0.5)

# ❌
# ✅
send_message2()
#schedule.every().day.at("00:21").do(send_message1)
#schedule.every().day.at("00:57").do(parser.aa)
#schedule.every().day.at("00:59").do(parser.aaa)

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