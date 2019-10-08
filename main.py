from waitress import serve
from flask import Flask, request, render_template, redirect, abort, Markup
import sqlite3
from urllib.parse import urlparse
import os
import qrcode
import base64
from PIL import Image
from io import BytesIO
import io

app = Flask(__name__)
domain_to_index = {}
domain_prepared = ""

try:
    domain = os.environ["domains"].split(";") #Get the domains from the enviorement variable. If no envioremenr variable is set set it to 127.0.0.1:5000 (normaly for testing only)
except:
    domain = ["127.0.0.1:5000"]

builddate = ""
try:
    if(os.environ["show_build_date"] == "1"): #If you want to see the builddate you can enable this enviorement variable
        builddate = ", Build date: " + open("builddate.txt", "r").read()
except:
    pass

index = 0
for domains in domain: #Make from every domnain a entry for the select box later
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
        try: #Try making the database structure, if fails Database was already created.
            cursor.execute(create_table)
        except sqlite3.OperationalError:
            pass


def makeQR(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    with BytesIO() as buffer:
        img.save(buffer, 'jpeg')
        return base64.b64encode(buffer.getvalue()).decode()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST': #Post will be executed if the client inserts a new entry
        if (request.form.get('url').replace(" ", "") == ""):
            return render_template('home.html', builddate=builddate, domain=domain_prepared, snackbar="Please enter a url to short, before submitting this form", long_url_prefilled=request.form.get('url'), short_url_prefilled=request.form.get('short'), domain_prefilled=domain_to_index[request.form.get('domain')]) #return the user the prefilled form with an error message, because no url to short was provided
        if (request.form.get('short').replace(" ", "") == ""):
            return render_template('home.html', builddate=builddate, domain=domain_prepared, snackbar="Please enter a short name, before submitting this form", long_url_prefilled=request.form.get('url'), short_url_prefilled=request.form.get('short'), domain_prefilled=domain_to_index[request.form.get('domain')]) #return the user the prefilled form with an error message, because no short link was provided
        shorturl = request.form.get('domain') + "/" + request.form.get('short')
        url = str.encode(request.form.get('url'))
        with sqlite3.connect('db/urls.db') as conn: #Check if another user already used the short link
            cursor = conn.cursor()
            res = cursor.execute('SELECT LONG_URL FROM WEB_URL WHERE SHORT_URL=?', [shorturl])
            try:
                short = res.fetchone()
                already_used = False
                if short is not None:
                    already_used = True
            except:
                pass

            if not already_used: #If short link wasn't used before, insert the link in the Database.
                res = cursor.execute(
                    'INSERT INTO WEB_URL (LONG_URL, SHORT_URL) VALUES (?, ?)',
                    [url, shorturl]
                )
                return render_template('home.html', short_url=shorturl, builddate=builddate, domain=domain_prepared, qrcode=makeQR("http://" + shorturl)) #return the shorten link to the user
            else:
                return render_template('home.html', builddate=builddate, domain=domain_prepared, snackbar="URL already used, please try another one", long_url_prefilled=request.form.get('url'), short_url_prefilled=request.form.get('short'), domain_prefilled=domain_to_index[request.form.get('domain')]) #return the user the prefilled form with an error message, because the url was already used
    return render_template('home.html', builddate=builddate, domain=domain_prepared) #If request method is get, return the default site to create a new shorten link

@app.route('/favicon.ico') #There is no favicon, so fail.
def favicon():
    return redirect("/static/favicon.ico")

@app.route('/<short_url>')
def redirect_short_url(short_url):
    host = request.headers['Host']
    url = ""
    with sqlite3.connect('db/urls.db') as conn: #Get the original URL from the database
        cursor = conn.cursor()
        res = cursor.execute('SELECT LONG_URL FROM WEB_URL WHERE SHORT_URL=?', [host + "/" + short_url])
        try:
            short = res.fetchone()
            if short is not None: #If a long url is found
                url = short[0]
                error_404 = False
            else:
                error_404 = True #If no url is found throw a 404, the problem is, if I throw at this point a 404 it will be catched by the try, catch block.
        except Exception as e: #If there happens an error, print the exception to the console and throw a 500 error
            print(e)
            abort(500)
    if not error_404: #If there was no 404 error before, redirect the user. If not throw a 404 error
        return redirect(url)
    else:
        abort(404)


if __name__ == '__main__':
    table_check()# This code checks whether database table is created or not
    serve(app, host='0.0.0.0', port= 5000) #Start the Webserver for all users on port 5000
