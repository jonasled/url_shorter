import sqlite3
import os
def table_check(): #Check if database exists
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
        file = open("import.csv", "r").readlines() #try opening file and read all lines
    except:
        print("no file for import found") #If open fails, there was no file.
        exit()
    entries = len(file) #Count the entries (for the output in the for loop)
    counter = 1
    for lines in file:
        print("Importing " + str(counter) + " from " + str(entries)) #Make a progress message (mormaly unnecessary, because import is to quick (<1s))
        SHORT_URL = lines.split(";")[0].replace("\n", "").replace("\r","") #Split the CSV at the ";" then use the first one and replace all linebreaks
        LONG_URL = lines.split(";")[1].replace("\n", "").replace("\r","") #Split the CSV at the ";" then use the seccond one and replace all linebreaks
        res = cursor.execute( #Insert the data in the SQL table
            'INSERT INTO WEB_URL (LONG_URL, SHORT_URL) VALUES (?, ?)',
            [LONG_URL, SHORT_URL]
        )
        counter = counter + 1 #Add 1 to counter, for progress