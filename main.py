from waitress import serve
from flask import Flask, request, render_template, redirect, abort, Markup
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3
from urllib.parse import urlparse
str_encode = str.encode
from string import ascii_lowercase
from string import ascii_uppercase
import base64
import os

# Assuming urls.db is in your app root folder
app = Flask(__name__)
domain = os.environ["domains"].split(";")
domain_prepared = ""

builddate = ""

if(os.environ["show_build_date"] == "1"):
    builddate = ", Build date: " + open("builddate.txt", "r").read()



for domains in domain:
    domains = domains
    domain_prepared = domain_prepared + '<option value="' + str(domains) + '">' + str(domains) + '</option>'

def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        LONG_URL TEXT NOT NULL, SHORT_URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('db/urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


def toBase62(num, b=62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + ascii_lowercase + ascii_uppercase
    r = num % b
    res = base[r]
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def toBase10(num, b=62):
    base = string.digits + ascii_lowercase + ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res


@app.route('/', methods=['GET', 'POST'])
def home():
    host = request.headers['Host']
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
        with sqlite3.connect('db/urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO WEB_URL (LONG_URL, SHORT_URL) VALUES (?, ?)',
                [base64.urlsafe_b64encode(url), request.form.get('domain') + "/" + request.form.get('short')]
            )
        return render_template('home.html', short_url=request.form.get('domain') + "/" + request.form.get('short'), builddate=builddate, domain=domain_prepared)
    return render_template('home.html', builddate=builddate, domain=domain_prepared)

@app.route('/favicon.ico')
def throw404():
    abort(404)

@app.route('/<short_url>')
def redirect_short_url(short_url):
    host = request.headers['Host']
    url = ""
    with sqlite3.connect('db/urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT LONG_URL FROM WEB_URL WHERE SHORT_URL=?', [host + "/" + short_url])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as e:
            print(e)
            abort(500)
    if(url == ""):
        abort(404)
    else:
        return redirect(url)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    serve(app, host='0.0.0.0', port= 5000)
