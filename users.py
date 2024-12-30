from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def users():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('users.html', users=[])

    try:
        cursor = connection.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        users = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('users.html', users=users)

def user_action():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    action = request.form.get('action')
    role = session.get('role')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('users'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action == 'add':
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            age = request.form.get('age')
            gender = request.form.get('gender')


            if not user_id or not name or not email or not password or not age or not gender:
                flash("All fields are required.", "warning")
                return redirect(url_for('users'))

            if user_id:
                cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
                existing_user = cursor.fetchone()

                if existing_user:
                    cursor.execute("SELECT user_id FROM users")
                    used_ids = {row['user_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new User ID is already in use. Please provide a unique ID. Suggestions: {suggestions}","warning")
                    return redirect(url_for('users'))

                query = 'INSERT INTO users (user_id, name, email, password, age, gender) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (user_id, name, email, password, age, gender))
            else:
                query = 'INSERT INTO users (user_id, name, email, password, age, gender) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (user_id, name, email, password, age, gender))
            connection.commit()
            flash("User added successfully!", "success")

        elif action == 'delete':
            selected_ids = request.form.get('selected_users')
            if not selected_ids:
                flash("No user(s) selected for deletion.", "warning")
                return redirect(url_for('users'))

            selected_ids = selected_ids.split(',')


            query = "DELETE FROM users WHERE user_id IN (%s)" % ','.join(['%s'] * len(selected_ids))
            cursor.execute(query, selected_ids)

            connection.commit()
            flash(f"Successfully deleted {cursor.rowcount} user(s).", "success")

        elif action == 'update':
            update_user_id = request.form.get('update_user_id')
            new_user_id = request.form.get('user_id')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            age = request.form.get('age')
            gender = request.form.get('gender')

            if not update_user_id:
                flash("No user selected for update.", "warning")
                return redirect(url_for('users'))

            if new_user_id != update_user_id:
                cursor.execute("SELECT COUNT(*) AS count FROM users WHERE user_id = %s", (new_user_id,))
                result = cursor.fetchone()
                if result['count'] > 0:
                    cursor.execute("SELECT user_id FROM users")
                    used_ids = {row['user_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new User ID is already in use. Please provide a unique ID. Suggestions: {suggestions}", "warning")
                    return redirect(url_for('users'))

            query = "UPDATE users SET user_id = %s, name = %s, email = %s, password = %s, age = %s, gender = %s WHERE user_id = %s"
            cursor.execute(query, (new_user_id, name, email, password, age, gender, update_user_id))
            connection.commit()
            flash("User updated successfully!", "success")

        elif action == 'filter':
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            age = request.form.get('age')
            gender = request.form.get('gender')

            if not any([user_id, name, email, password, age, gender]):
                flash("Please provide at least one filter criteria.", "warning")
                return redirect(url_for('users'))

            query = "SELECT * FROM users WHERE 1=1"
            params = []

            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            if name:
                query += " AND name = %s"
                params.append(name)
            if email:
                query += " AND email = %s"
                params.append(email)
            if password:
                query += " AND password = %s"
                params.append(password)
            if age:
                query += " AND age = %s"
                params.append(age)
            if gender:
                query += " AND gender = %s"
                params.append(gender)

            cursor.execute(query, params)
            users = cursor.fetchall()
            session['filtered_users'] = users
            flash(f"Found {len(users)} user(s) matching the criteria(s).", "success")
            return render_template('users.html', users=users)

        elif action == 'sort':
            sort_by = request.form.get('sort_by')
            sort_order = request.form.get('sort_order')

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('users'))

            if 'filtered_users' in session and session['filtered_users']:
                filtered_ids = [user['user_id'] for user in session['filtered_users']]

                query = f"SELECT * FROM users WHERE user_id IN ({','.join(['%s'] * len(filtered_ids))}) ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, filtered_ids)
                users = cursor.fetchall()

                flash("Filtered users sorted successfully!", "success")
            else:
                query = "SELECT * FROM users WHERE 1=1"
                params = []

                query += f" ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, params)
                users = cursor.fetchall()
                flash("Users sorted successfully!", "success")

            return render_template('users.html', users=users)

        elif action == 'clear':
            if 'filtered_users' in session:
                session.pop('filtered_users', None)

            query = "SELECT * FROM users"
            params = []

            cursor.execute(query, params)
            users = cursor.fetchall()
            flash("All filters, sorting, and selections have been cleared.", "success")
            return render_template('users.html', users=users)
    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('users'))

