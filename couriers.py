from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def couriers():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')
    restaurant_id = session.get('restaurant_id')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('couriers.html', couriers=[])

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

            if role == 'user' and restaurant_id != str(restaurant_id_session):
                flash("Unauthorized action! You can only add courier(s) for your restaurant.", "danger")
                return redirect(url_for('couriers'))

            if not name or not gender or not birth_date or not restaurant_id:
                flash("All fields are required (except Courier ID).", "warning")
                return redirect(url_for('couriers'))

            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone() #################################################

            if result['COUNT(*)'] == 0:
                flash('No restaurant found with that Restaurant ID!', 'danger')
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

            if role == 'user' and (restaurant_id != str(restaurant_id_session) or new_courier_id != update_courier_id):
                flash("Unauthorized action! You cannot change your Courier's ID or Restaurant ID.", "danger")
                return redirect(url_for('couriers'))

            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone()

            if result['COUNT(*)'] == 0:
                # If the Restaurant ID is not found, flash an error message
                flash('No restaurant found with that Restaurant ID!', 'danger')
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

            query = "UPDATE couriers SET courier_id = %s, name = %s, gender = %s, birth_date = %s, restaurant_id = %s WHERE courier_id = %s"
            cursor.execute(query, (new_courier_id, name, gender, birth_date, restaurant_id, update_courier_id))
            connection.commit()
            flash("Courier updated successfully!", "success")

        elif action == 'filter':
            courier_id = request.form.get('courier_id')
            name = request.form.get('name')
            gender = request.form.get('gender')
            birth_date = request.form.get('birth_date')
            restaurant_id = request.form.get('restaurant_id')

            if not any([courier_id, name, gender, birth_date, restaurant_id]):
                flash("Please provide at least one filter criteria.", "warning")
                return redirect(url_for('couriers'))

            query = "SELECT * FROM couriers WHERE 1=1"
            params = []
            if role == 'user':
                query += " AND restaurant_id = %s"
                params.append(restaurant_id_session)

            if courier_id:
                query += " AND courier_id = %s"
                params.append(courier_id)
            if name:
                query += " AND name LIKE %s"
                params.append(f"%{name}%")
            if gender:
                query += " AND gender = %s"
                params.append(gender)
            if birth_date:
                query += " AND birth_date = %s"
                params.append(birth_date)
            if restaurant_id:
                query += " AND restaurant_id = %s"
                params.append(restaurant_id)

            cursor.execute(query, params)
            couriers = cursor.fetchall()
            session['filtered_couriers'] = couriers
            flash(f"Found {len(couriers)} courier(s) matching the criteria(s).", "success")
            return render_template('couriers.html', couriers=couriers)

        elif action == 'sort':
            sort_by = request.form.get('sort_by')
            sort_order = request.form.get('sort_order')

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('couriers'))

            if 'filtered_couriers' in session and session['filtered_couriers']:
                filtered_ids = [courier['courier_id'] for courier in session['filtered_couriers']]

                query = f"SELECT * FROM couriers WHERE courier_id IN ({','.join(['%s'] * len(filtered_ids))}) ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, filtered_ids)
                couriers = cursor.fetchall()

                flash("Filtered couriers sorted successfully!", "success")
            else:
                query = "SELECT * FROM couriers WHERE 1=1"
                params = []
                if role == 'user':
                    query += " AND restaurant_id = %s"
                    params.append(restaurant_id_session)

                query += f" ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, params)
                couriers = cursor.fetchall()
                flash("Couriers sorted successfully!", "success")

            return render_template('couriers.html', couriers=couriers)

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
