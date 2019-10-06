import sqlite3
import os
def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        LONG_URL TEXT NOT NULL, SHORT_URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('db/urls.db') as conn:
        cursor = conn.cursor()
        try: #Try making the database structure, if fails Database was already created.
            cursor.execute(create_table)
        except sqlite3.OperationalError:
            pass


table_check()
with sqlite3.connect('db/urls.db') as conn:
    cursor = conn.cursor()
    try:
        file = open("import.csv", "r").readlines()
    except:
        print("no file for import found")
        exit()
    entries = len(file)
    counter = 1
    for lines in file:
        print("Importing " + str(counter) + " from " + str(entries))
        SHORT_URL = lines.split(";")[0].replace("\n", "").replace("\r","")
        LONG_URL = lines.split(";")[1].replace("\n", "").replace("\r","")
        res = cursor.execute(
            'INSERT INTO WEB_URL (LONG_URL, SHORT_URL) VALUES (?, ?)',
            [LONG_URL, SHORT_URL]
        )
        counter = counter + 1
    os.system("exit")