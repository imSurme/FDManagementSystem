from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        if connection is None:
            flash("Couldn't connect to the database!", "danger")
            return render_template('login.html')

        try:
            cursor = connection.cursor(dictionary=True)
            if role == 'admin':
                cursor.execute('SELECT * FROM admins WHERE email = %s AND password = %s', (email, password))
                admin = cursor.fetchone()

                if admin and admin['email'] == email and admin['password'] == password:
                    session['logged_in'] = True
                    session['role'] = 'admin'
                    flash("Admin login successful!", "success")
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email or password', 'danger')

            elif role == 'user':
                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
                user = cursor.fetchone()

                if user and user['email'] == email and user['password'] == password:
                    session['user_id'] = user['user_id']
                    cursor.execute('SELECT * FROM restaurants WHERE user_id = %s', (session['user_id'],))
                    restaurant = cursor.fetchone()

                    if restaurant:
                        session['logged_in'] = True
                        session['role'] = 'user'
                        session['restaurant_id'] = restaurant['restaurant_id']
                        flash("Restaurant Owner login successful!", "success")
                        return redirect(url_for('index'))
                    else:
                        flash("Invalid email or password.", "danger")
                else:
                    flash("Invalid email or password.", "danger")
        except Error as e:
            flash(f"Query failed: {e}", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('login.html')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))