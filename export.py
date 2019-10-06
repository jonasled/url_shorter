# to run this script and export the database from an docker container run docker -it <container_name> python3 export.py > database.csv
#The output will be in excel-style CSV (";" instead of "," as column seperator.)

import sqlite3

create_table = """
    CREATE TABLE WEB_URL(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    LONG_URL TEXT NOT NULL, SHORT_URL TEXT NOT NULL
    );
    """
with sqlite3.connect('db/urls.db') as conn:
    cursor = conn.cursor()
    try: #Try making the database structure, if succeeded, exit, because there can't be any data.
        cursor.execute(create_table)
        print("No data Found, exiting")
        exit()
    except sqlite3.OperationalError:
        pass

conn = sqlite3.connect('db/urls.db')
cursor = conn.cursor()
res = cursor.execute('SELECT LONG_URL, SHORT_URL FROM WEB_URL WHERE 1') #read all data from database
for entries in res.fetchall():
    print(str(entries[1]) + ";" + str(entries[0])) #format the data and print it to console.