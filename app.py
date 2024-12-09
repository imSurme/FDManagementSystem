from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'a_secret_key'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="fill_here",
            user="fill_here",
            passwd="fill_here",
            database="fill_here"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        if connection is None:
            flash("Couldn't connect to the database!", "danger")
            return render_template('login.html')

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM admins WHERE email = %s AND password = %s', (email, password))
            admin = cursor.fetchone()

            if admin and admin['email'] == email and admin['password'] == password:
                session['logged_in'] = True
                flash("Admin login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'danger')
        except Error as e:
            flash(f"Query failed: {e}", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/couriers')
def couriers():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('index.html', couriers=[])

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM couriers')
        couriers = cursor.fetchall()
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        couriers = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('couriers.html', couriers=couriers)

@app.route('/restaurants')
def restaurants():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('index.html', restaurants=[])

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM restaurants')
        restaurants = cursor.fetchall()
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        restaurants = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('restaurants.html', restaurants=restaurants)

if __name__ == '__main__':
    app.run(debug=True)
