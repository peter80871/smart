import datetime
import db

def today_match(day):
    d = list(set(db.show_data_in_table('UPCOMING_MATCHES')))

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=day)
    dd = str(tomorrow)
    tomorrow = str(tomorrow).split('-')
    upcoming_matches = [i for i in d if i[3].split('.')[0] == tomorrow[2] and i[3].split('.')[1] == tomorrow[1]]

    return upcoming_matches, dd