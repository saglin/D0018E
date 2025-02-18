#!/bin/python3

from flask import Flask, render_template, jsonify, request, session, url_for, redirect
from flask_mysqldb import MySQL
import random

app = Flask(__name__)

app.secret_key = 'SECRET_KEY'

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
    return render_template("item.html", id=data[0], item=data[1], price=data[2], stock=data[3], description=data[4])

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")


# Check if the username and password are legitimate
@app.route("/check_credentials", methods=['POST'])
def check_credentials():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM User WHERE User.username=%s and User.encrypted_password=%s''', (username,password,))
        data = cursor.fetchone()
        cursor.close()
        if data != None:
            session['user_id'] = data[0]
            if data[8]: # Checks if the user is an admin
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else: 
            return redirect(url_for('login'))

@app.route("/add_to_cart/<int:id>", methods=['POST'])
def add_to_cart(id):
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO Shopping_Cart (user_id, item_id, item_amount) VALUES (%i, %i, 1)''', (session['user_id'], id))
        cursor.close()
        return redirect(url_for('item_page', id=id))


app.run(host="0.0.0.0", port=80)
