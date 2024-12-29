from flask import render_template, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    role = session.get('role')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('index.html', statistics=[])

    statistics = {
        'users': 0,
        'restaurants': 0,
        'menus': 0,
        'foods': 0,
        'orders': 0,
        'couriers': 0
    }

    try:
        cursor = connection.cursor(dictionary=True)

        if role == 'admin':
            queries = {
                'users': "SELECT COUNT(*) AS count FROM users",
                'restaurants': "SELECT COUNT(*) AS count FROM restaurants",
                'menus': "SELECT COUNT(*) AS count FROM menus",
                'foods': "SELECT COUNT(*) AS count FROM foods",
                'orders': "SELECT COUNT(*) AS count FROM orders",
                'couriers': "SELECT COUNT(*) AS count FROM couriers"
            }
        elif role == 'user':
            user_id = session.get('user_id')
            restaurant_id = session.get('restaurant_id')

            queries = {
                'menus': f"SELECT COUNT(*) AS count FROM menus WHERE restaurant_id = {restaurant_id}",
                'foods': f"""
                    SELECT COUNT(DISTINCT f.food_id) AS count
                    FROM foods f
                    JOIN menus m ON f.food_id = m.food_id
                    JOIN restaurants r ON m.restaurant_id = r.restaurant_id
                    WHERE r.user_id = {user_id}
                """,
                'orders': f"SELECT COUNT(*) AS count FROM orders WHERE restaurant_id = {restaurant_id}",
                'couriers': f"SELECT COUNT(*) AS count FROM couriers WHERE restaurant_id = {restaurant_id}",
            }

        for key, query in queries.items():
            cursor.execute(query)
            result = cursor.fetchone()
            statistics[key] = result['count'] if result and 'count' in result else 0
            print(f"Role: {role}")
            print(f"Statistics: {statistics}")
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        statistics = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('index.html', role=role, statistics=statistics)
