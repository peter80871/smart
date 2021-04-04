import sqlite3


def db_create():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE "PREDICTED_MATCHES" (country TEXT, league TEXT, team1 TEXT, team2 TEXT, date TEXT, time TEXT, win_team TEXT, t TEXT, kf TEXT);''')
    c.execute('CREATE TABLE "TEAM_IN_LEAGUES" (country TEXT, league TEXT, team TEXT);')
    c.execute(
        'CREATE TABLE "ALL_MATCHES" (league TEXT, series TEXT, team TEXT, team1 TEXT, team2 TEXT, t1 INTEGER, t2 INTEGER, date TEXT, t INTEGER);')
    c.execute('CREATE TABLE "UPCOMING_MATCHES" (league TEXT, team1 TEXT, team2 TEXT,  date TEXT);')
    conn.commit()
    conn.close()


def db_drop(table):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(f"DROP TABLE {table};")

    if table == "UPCOMING_MATCHES":
        c.execute(
            'CREATE TABLE "UPCOMING_MATCHES" (league TEXT, team1 TEXT, team2 TEXT,  date TEXT, date2 TEXT);'
        )

    elif table == "ALL_MATCHES":
        c.execute(
            'CREATE TABLE "ALL_MATCHES" (league TEXT, series TEXT, team TEXT, team1 TEXT, team2 TEXT, t1 INTEGER, t2 INTEGER, date TEXT, t INTEGER);'
        )

    elif table == "PREDICTED_MATCHES":
        c.execute(
            'CREATE TABLE "PREDICTED_MATCHES" (country TEXT, league TEXT, team1 TEXT, team2 TEXT, date TEXT, time TEXT, win_team TEXT, t TEXT, kf TEXT);'
        )

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

    tables = [i[1] for i in tables]

    return tables


def show_data_in_table(table):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(f'SELECT * FROM "{table}"')

    c = c.fetchmany(2000)
    conn.close()

    return c

# print(show_tables())
# print(show_data_in_table('PREDICTED_MATCHES'))
