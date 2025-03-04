#!/bin/python3

from flask import Flask, render_template, jsonify, request, session, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
import numpy

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
    item_data = cursor.fetchone()
    cursor.execute('''SELECT User.username, Comment.time_posted, Comment.comment_text FROM Comment, User WHERE Comment.item_id=%s AND User.id=Comment.user_id''', (id,))
    comment_data = cursor.fetchall()
    cursor.execute('''SELECT Rating.star_rating FROM Rating WHERE Rating.item_id=%s''', (id,))
    rating_data = cursor.fetchall()
    average_rating = numpy.mean(rating_data)
    cursor.close()
    return render_template("item.html", id=item_data[0], item=item_data[1], price=item_data[2], stock=item_data[3], description=item_data[4], comments=comment_data, average_rating=average_rating)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin")
def admin():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Item''')
    items = cursor.fetchall()
    cursor.execute('''SELECT * FROM Orders''')
    orders = cursor.fetchall()
    cursor.close()
    return render_template("admin.html", items=items, orders=orders)


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
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('''INSERT INTO Shopping_Cart (user_id, item_id, item_amount) VALUES (%s, %s, 1)''', (session['user_id'], id,))
            mysql.connection.commit()
            cursor.close()
        except:
            pass
        return redirect(url_for('item_page', id=id))


@app.route("/add_new_item", methods=['POST'])
def add_new_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        price = request.form['price']
        stock = request.form['stock']
        item_description = request.form['item_description']
        item_image = request.form['item_image']
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM Item''')
        id = len(cursor.fetchall()) + 1
        cursor.execute('''INSERT INTO Item (id, item_name, price, stock, item_description, item_image) VALUES (%s, %s, %s, %s, %s, %s)''', (id, item_name, price, stock, item_description, item_image,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('admin'))

@app.route("/change_stock/<int:id>", methods=['POST'])
def change_stock(id):
    if request.method == 'POST':
        stock = request.form['stock']
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE Item SET Item.stock=%s WHERE Item.id=%s''', (stock, id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('admin'))
    
@app.route("/shopping_cart")
def shopping_cart():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT Item.id, Item.item_name, Item.price, Shopping_Cart.item_amount FROM Item, Shopping_Cart WHERE Shopping_Cart.user_id=%s AND Item.id=Shopping_Cart.item_id''', (session['user_id'],))
    data = cursor.fetchall()
    return render_template("shopping_cart.html", data=data)

@app.route("/change_item_amount/<int:item_id>", methods=['POST'])
def change_item_amount(item_id):
    if request.method == 'POST':
        new_item_amount = request.form['new_item_amount']
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        if int(new_item_amount) > 0:
            cursor.execute('''SELECT Item.stock FROM Item WHERE Item.id=%s''', (item_id,))
            stock = cursor.fetchone()[0]
            if stock < int(new_item_amount):
                cursor.close()
                return redirect(url_for('shopping_cart'))
            cursor.execute('''UPDATE Shopping_Cart SET Shopping_Cart.item_amount=%s WHERE Shopping_Cart.user_id=%s AND Shopping_Cart.item_id=%s''', (new_item_amount, user_id, item_id, ))
        else:
            cursor.execute('''DELETE FROM Shopping_Cart WHERE Shopping_Cart.user_id=%s AND Shopping_Cart.item_id=%s''', (user_id, item_id, ))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('shopping_cart'))
    
@app.route("/send_order/<int:id>", methods=['POST'])
def send_order(id):
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE Orders SET Orders.sent=1''')
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('admin'))
    
@app.route("/place_order", methods=['POST'])
def place_order():
    if request.method == 'POST':
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT Item.id, Item.price, Shopping_Cart.item_amount FROM Item, Shopping_Cart WHERE Shopping_Cart.user_id=%s AND Item.id=Shopping_Cart.item_id''', (session['user_id'],))
        data = cursor.fetchall()
        if len(data) > 0:
            cursor.execute('''SELECT * FROM Orders''')
            order_id = len(cursor.fetchall()) + 1
            date_placed = str(date.today())
            cursor.execute('''INSERT INTO Orders (id, user_id, date_placed, sent) VALUES (%s, %s, %s, 0)''', (order_id, user_id, date_placed,))
            for i in range(len(data)):
                item_id = data[i][0]
                item_price = data[i][1]
                item_amount = data[i][2]
                cursor.execute('''INSERT INTO Order_Items (item_id, order_id, item_amount, price) VALUES (%s, %s, %s, %s)''', (item_id, order_id, item_amount, item_price,))
                cursor.execute('''SELECT Item.stock FROM Item WHERE Item.id=%s''', (item_id, ))
                stock = cursor.fetchone()[0]
                if stock < item_amount:
                    cursor.close()
                    return redirect(url_for('shopping_cart'))
                cursor.execute('''UPDATE Item SET Item.stock=%s WHERE Item.id=%s''', (stock - item_amount, item_id, ))
            cursor.execute('''DELETE FROM Shopping_Cart WHERE Shopping_Cart.user_id=%s''', (user_id, ))
            mysql.connection.commit()
        cursor.close()
        return redirect(url_for('shopping_cart'))
    
@app.route("/leave_comment/<int:id>", methods=['POST'])
def leave_comment(id):
    if request.method == 'POST':
        user_id = session['user_id']
        new_comment = request.form['new_comment']
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM Comment''')
        comment_id = len(cursor.fetchall()) + 1
        time_posted = str(date.today())
        cursor.execute('''INSERT INTO Comment (id, user_id, time_posted, item_id, comment_text) VALUES (%s, %s, %s, %s, %s)''', (comment_id, user_id, time_posted, id, new_comment))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('item_page', id=id))
    
@app.route("/leave_rating/<int:id>", methods=['POST'])
def leave_rating(id):
    if request.method == 'POST':
        user_id = session['user_id']
        new_rating = request.form['rating']
        cursor = mysql.connection.cursor()
        cursor.execute('''DELETE FROM Rating WHERE Rating.user_id=%s AND Rating.item_id=%s''', (user_id, id,))
        cursor.execute('''INSERT INTO Rating (user_id, item_id, star_rating) VALUES (%s, %s, %s)''', (user_id, id, new_rating))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('item_page', id=id))
    
@app.route("/register_user", methods=['POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        encrypted_password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone_number = request.form['phone_number']
        adress = request.form['adress']

        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM User WHERE User.email=%s''', (email,))
        data = cursor.fetchall()
        if len(data) != 0: # Already a registered user with this email
            cursor.close()
            return redirect(url_for('login')) 
        
        cursor.execute('''SELECT * FROM User WHERE User.username=%s''', (username,))
        data = cursor.fetchall()
        if len(data) != 0: # Some other user already has this username
            cursor.close()
            return redirect(url_for('register'))

        cursor.execute('''SELECT * FROM User''')
        user_id = len(cursor.fetchall()) + 1
        cursor.execute('''INSERT INTO User (id, username, encrypted_password, firstname, lastname, email, phone_number, adress, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)''', (user_id, username, encrypted_password, firstname, lastname, email, phone_number, adress,))
        mysql.connection.commit()
        cursor.close()

        session['user_id'] = user_id
        return redirect(url_for('index'))

app.run(host="0.0.0.0", port=80)
