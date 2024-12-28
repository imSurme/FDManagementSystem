from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error
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