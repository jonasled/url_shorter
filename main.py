from waitress import serve
from flask import Flask, request, render_template, redirect, abort, Markup
import sqlite3
from urllib.parse import urlparse
import os

str_encode = str.encode
app = Flask(__name__)
domain_to_index = {}
domain_prepared = ""

try:
    domain = os.environ["domains"].split(";")
except:
    domain = ["127.0.0.1:5000"]

builddate = ""
try:
    if(os.environ["show_build_date"] == "1"):
        builddate = ", Build date: " + open("builddate.txt", "r").read()
except:
    pass

index = 0
for domains in domain:
    domains = domains
    domain_prepared = domain_prepared + '<option value="' + str(domains) + '">' + str(domains) + '</option>'
    domain_to_index[domains] = str(index)
    index = index + 1


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
        except sqlite3.OperationalError:
            pass


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
            res = cursor.execute('SELECT LONG_URL FROM WEB_URL WHERE SHORT_URL=?', [request.form.get('domain') + "/" + request.form.get('short')])
            try:
                short = res.fetchone()
                already_used = False
                if short is not None:
                    already_used = True
            except Exception as e:
                pass

            if not already_used:
                res = cursor.execute(
                    'INSERT INTO WEB_URL (LONG_URL, SHORT_URL) VALUES (?, ?)',
                    [url, request.form.get('domain') + "/" + request.form.get('short')]
                )
                return render_template('home.html', short_url=request.form.get('domain') + "/" + request.form.get('short'), builddate=builddate, domain=domain_prepared)
            else:
                return render_template('home.html', builddate=builddate, domain=domain_prepared, alreadychoosen=True, long_url_prefilled=request.form.get('url'), short_url_prefilled=request.form.get('short'), domain_prefilled=domain_to_index[request.form.get('domain')])
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
                url = short[0]
                error_404 = False
            else:
                error_404 = True
        except Exception as e:
            print(e)
            abort(500)
    if not error_404:
        return redirect(url)
    else:
        abort(404)


if __name__ == '__main__':
    table_check()# This code checks whether database table is created or not
    serve(app, host='0.0.0.0', port= 5000)
