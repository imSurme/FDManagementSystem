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
                    user_id = user['user_id']
                    cursor.execute('SELECT * FROM restaurants WHERE user_id = %s', (user_id,))
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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/couriers')
def couriers():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    restaurant_id = session.get('restaurant_id')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('index.html', couriers=[])

    try:
        cursor = connection.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute('SELECT * FROM couriers')
            couriers = cursor.fetchall()
        elif role == 'user' and restaurant_id:
            cursor.execute('SELECT * FROM couriers WHERE restaurant_id = %s', (restaurant_id,))
            couriers = cursor.fetchall()
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        couriers = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('couriers.html', couriers=couriers)

@app.route('/courier_action', methods=['POST'])
def courier_action():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    action = request.form.get('action')
    role = session.get('role')
    restaurant_id_session = session.get('restaurant_id') if role == 'user' else None

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('couriers'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action == 'add':
            courier_id = request.form.get('courier_id')
            name = request.form.get('name')
            gender = request.form.get('gender')
            birth_date = request.form.get('birth_date')
            restaurant_id = request.form.get('restaurant_id')

            if not name or not gender or not birth_date or not restaurant_id:
                flash("All fields are required (except Courier ID).", "warning")
                return redirect(url_for('couriers'))

            if role == 'user' and restaurant_id != str(restaurant_id_session):
                flash("Unauthorized action! You can only manage couriers for your restaurant.", "danger")
                return redirect(url_for('couriers'))

            if courier_id:
                cursor.execute("SELECT courier_id FROM couriers WHERE courier_id = %s", (courier_id,))
                existing_courier = cursor.fetchone()

                if existing_courier:
                    cursor.execute("SELECT courier_id FROM couriers")
                    used_ids = {row['courier_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new Courier ID is already in use. Please provide a unique ID. Suggestions: {suggestions}","warning")
                    return redirect(url_for('couriers'))

                query = 'INSERT INTO couriers (courier_id, name, gender, birth_date, restaurant_id) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(query, (courier_id, name, gender, birth_date, restaurant_id))
            else:
                query = 'INSERT INTO couriers (name, gender, birth_date, restaurant_id) VALUES (%s, %s, %s, %s)'
                cursor.execute(query, (name, gender, birth_date, restaurant_id))
            connection.commit()
            flash("Courier added successfully!", "success")

        elif action == 'delete':
            selected_ids = request.form.get('selected_couriers')
            if not selected_ids:
                flash("No courier(s) selected for deletion.", "warning")
                return redirect(url_for('couriers'))

            selected_ids = selected_ids.split(',')

            if role == 'user':
                query = "DELETE FROM couriers WHERE courier_id IN ({}) AND restaurant_id = %s".format(','.join(['%s'] * len(selected_ids)))
                cursor.execute(query, selected_ids + [restaurant_id_session])
            else:
                query = "DELETE FROM couriers WHERE courier_id IN (%s)" % ','.join(['%s'] * len(selected_ids))
                cursor.execute(query, selected_ids)

            connection.commit()
            flash(f"Successfully deleted {cursor.rowcount} courier(s).", "success")

        elif action == 'update':
            update_courier_id = request.form.get('update_courier_id')
            new_courier_id = request.form.get('courier_id')
            name = request.form.get('name')
            gender = request.form.get('gender')
            birth_date = request.form.get('birth_date')
            restaurant_id = request.form.get('restaurant_id')

            if not update_courier_id:
                flash("No courier selected for update.", "warning")
                return redirect(url_for('couriers'))

            if role == 'user' and restaurant_id != str(restaurant_id_session):
                flash("Unauthorized action! You can only manage couriers for your restaurant.", "danger")
                return redirect(url_for('couriers'))

            if new_courier_id != update_courier_id:
                cursor.execute("SELECT COUNT(*) AS count FROM couriers WHERE courier_id = %s", (new_courier_id,))
                result = cursor.fetchone()
                if result['count'] > 0:
                    cursor.execute("SELECT courier_id FROM couriers")
                    used_ids = {row['courier_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new Courier ID is already in use. Please provide a unique ID. Suggestions: {suggestions}","warning")
                    return redirect(url_for('couriers'))

            query = "UPDATE couriers SET name = %s, gender = %s, birth_date = %s, restaurant_id = %s WHERE courier_id = %s"
            cursor.execute(query, (name, gender, birth_date, restaurant_id, update_courier_id))
            connection.commit()
            flash("Courier updated successfully!", "success")

        elif action == 'clear':
            if 'filtered_couriers' in session:
                session.pop('filtered_couriers', None)

            query = "SELECT * FROM couriers"
            params = []
            if role == 'user':
                query += " WHERE restaurant_id = %s"
                params.append(restaurant_id_session)

            cursor.execute(query, params)
            couriers = cursor.fetchall()
            flash("All filters, sorting, and selections have been cleared.", "success")
            return render_template('couriers.html', couriers=couriers)
    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('couriers'))

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
