#!/bin/python3

from flask import Flask, render_template, jsonify, request, session
from flask_mysqldb import MySQL
import random

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'databas'
mysql = MySQL(app)

@app.route("/browse")
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Item''')
    data = cursor.fetchall()
    cursor.close()
    return render_template("index.html", items=data)

@app.route("/item/<int:id>")
def item_page(id):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Item WHERE Item.id=%s''', (id,))
    data = cursor.fetchone()
    cursor.close()
    return render_template("item.html", item=data[1], price=data[2], stock=data[3], description=data[4])

@app.route("/", methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM User WHERE User.username=%s and User.password=%s''', (username,password,))
        data = cursor.fetchone()
        cursor.close()
        if len(data) == 1:
            session['user_id'] == data.id
            return index()
        else: 
            return login()
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")


# Check if the username and password are legitimate
@app.route("/check_credentials/<string:username>/<string:password>")
def check_credentials(username, password):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM User WHERE User.username=%s and User.password=%s''', (username,password,))
    data = cursor.fetchone()
    cursor.close()
    if len(data) == 1:
        return index()
    else:
        return login()

app.run(host="0.0.0.0", port=80)
