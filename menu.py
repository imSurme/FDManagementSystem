from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')
    restaurant_id = session.get('restaurant_id')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('menu.html', menu=[])

    try:
        cursor = connection.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute('''
                SELECT m.*, f.item_name as food_name 
                FROM menu m 
                LEFT JOIN food f ON m.food_id = f.food_id
            ''')
            menu = cursor.fetchall()
        elif role == 'user' and restaurant_id:
            cursor.execute('''
                SELECT m.*, f.item_name as food_name 
                FROM menu m 
                LEFT JOIN food f ON m.food_id = f.food_id 
                WHERE m.restaurant_id = %s
            ''', (restaurant_id,))
            menu = cursor.fetchall()
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))

        # Transform the menu items to use food_name when available
        for item in menu:
            if item['food_name']:
                item['name'] = item['food_name']
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        menu = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('menu.html', menu=menu)

def menu_action():
    if 'logged_in' not in session:
        return redirect(url_for('menu'))

    action = request.form.get('action')
    role = session.get('role')
    restaurant_id_session = session.get('restaurant_id') if role == 'user' else None

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('menu'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action == 'add':
            menu_id = request.form.get('menu_id')
            food_id = request.form.get('food_id')
            price = request.form.get('price')
            restaurant_id = request.form.get('restaurant_id')

            if role == 'user' and restaurant_id != str(restaurant_id_session):
                flash("Unauthorized action! You can only add menu item(s) for your restaurant.", "danger")
                return redirect(url_for('menu'))

            if not food_id or not price or not restaurant_id:
                flash("All fields are required (except Menu ID).", "warning")
                return redirect(url_for('menu'))

            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone()

            if result['COUNT(*)'] == 0:
                flash('No restaurant found with that Restaurant ID!', 'danger')
                return redirect(url_for('menu'))

            if menu_id:
                cursor.execute("SELECT menu_id FROM menu WHERE menu_id = %s", (menu_id,))
                existing_menu = cursor.fetchone()

                if existing_menu:
                    cursor.execute("SELECT menu_id FROM menu")
                    used_ids = {row['menu_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new Menu ID is already in use. Please provide a unique ID. Suggestions: {suggestions}", "warning")
                    return redirect(url_for('menu'))

                query = 'INSERT INTO menu (menu_id, food_id, price, restaurant_id) VALUES (%s, %s, %s, %s)'
                cursor.execute(query, (menu_id, food_id, price, restaurant_id))
            else:
                query = 'INSERT INTO menu (food_id, price, restaurant_id) VALUES (%s, %s, %s)'
                cursor.execute(query, (food_id, price, restaurant_id))
            connection.commit()
            flash("Menu item added successfully!", "success")

        elif action == 'delete':
            selected_ids = request.form.get('selected_menu_items')
            if not selected_ids:
                flash("No menu item(s) selected for deletion.", "warning")
                return redirect(url_for('menu'))

            selected_ids = selected_ids.split(',')

            if role == 'user':
                query = "DELETE FROM menu WHERE menu_id IN ({}) AND restaurant_id = %s".format(','.join(['%s'] * len(selected_ids)))
                cursor.execute(query, selected_ids + [restaurant_id_session])
            else:
                query = "DELETE FROM menu WHERE menu_id IN (%s)" % ','.join(['%s'] * len(selected_ids))
                cursor.execute(query, selected_ids)

            connection.commit()
            flash(f"Successfully deleted {cursor.rowcount} menu item(s).", "success")

        elif action == 'update':
            update_menu_id = request.form.get('update_menu_id')
            new_menu_id = request.form.get('menu_id')
            food_id = request.form.get('food_id')
            price = request.form.get('price')
            restaurant_id = request.form.get('restaurant_id')

            if not update_menu_id:
                flash("No menu item selected for update.", "warning")
                return redirect(url_for('menu'))

            if role == 'user' and (restaurant_id != str(restaurant_id_session) or new_menu_id != update_menu_id):
                flash("Unauthorized action! You cannot change your Menu Item's ID or Restaurant ID.", "danger")
                return redirect(url_for('menu'))

            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone()

            if result['COUNT(*)'] == 0:
                flash('No restaurant found with that Restaurant ID!', 'danger')
                return redirect(url_for('menu'))

            if new_menu_id != update_menu_id:
                cursor.execute("SELECT COUNT(*) AS count FROM menu WHERE menu_id = %s", (new_menu_id,))
                result = cursor.fetchone()
                if result['count'] > 0:
                    cursor.execute("SELECT menu_id FROM menu")
                    used_ids = {row['menu_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new Menu ID is already in use. Please provide a unique ID. Suggestions: {suggestions}", "warning")
                    return redirect(url_for('menu'))

            query = "UPDATE menu SET menu_id = %s, food_id = %s, price = %s, restaurant_id = %s WHERE menu_id = %s"
            cursor.execute(query, (new_menu_id, food_id, price, restaurant_id, update_menu_id))
            connection.commit()
            flash("Menu item updated successfully!", "success")

        elif action == 'filter':
            menu_id = request.form.get('menu_id')
            food_name = request.form.get('name')
            price = request.form.get('price')
            restaurant_id = request.form.get('restaurant_id')

            if not any([menu_id, food_name, price, restaurant_id]):
                flash("Please provide at least one filter criteria.", "warning")
                return redirect(url_for('menu'))

            query = """
                SELECT m.*, f.item_name as food_name 
                FROM menu m 
                LEFT JOIN food f ON m.food_id = f.food_id 
                WHERE 1=1
            """
            params = []
            if role == 'user':
                query += " AND restaurant_id = %s"
                params.append(restaurant_id_session)

            if menu_id:
                query += " AND m.menu_id = %s"
                params.append(menu_id)
            if food_name:
                query += " AND f.item_name LIKE %s"
                params.append(f"%{food_name}%")
            if price:
                query += " AND price = %s"
                params.append(price)
            if restaurant_id:
                query += " AND m.restaurant_id = %s"
                params.append(restaurant_id)

            cursor.execute(query, params)
            menu = cursor.fetchall()
            # Transform the menu items to use food_name when available
            for item in menu:
                if item['food_name']:
                    item['name'] = item['food_name']
            session['filtered_menu'] = menu
            flash(f"Found {len(menu)} menu item(s) matching the criteria(s).", "success")
            return render_template('menu.html', menu=menu)

        elif action == 'sort':
            sort_by = request.form.get('sort_by')
            sort_order = request.form.get('sort_order')

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('menu'))

            if 'filtered_menu' in session and session['filtered_menu']:
                filtered_ids = [item['menu_id'] for item in session['filtered_menu']]

                query = f"""
                    SELECT m.*, f.item_name as food_name 
                    FROM menu m 
                    LEFT JOIN food f ON m.food_id = f.food_id 
                    WHERE m.menu_id IN ({','.join(['%s'] * len(filtered_ids))}) 
                    ORDER BY COALESCE(f.item_name, m.name) {sort_order}
                """ if sort_by == 'name' else f"""
                    SELECT m.*, f.item_name as food_name 
                    FROM menu m 
                    LEFT JOIN food f ON m.food_id = f.food_id 
                    WHERE m.menu_id IN ({','.join(['%s'] * len(filtered_ids))}) 
                    ORDER BY m.{sort_by} {sort_order}
                """
                cursor.execute(query, filtered_ids)
                menu = cursor.fetchall()

                # Transform the menu items to use food_name when available
                for item in menu:
                    if item['food_name']:
                        item['name'] = item['food_name']

                flash("Filtered menu items sorted successfully!", "success")
            else:
                query = "SELECT * FROM menu WHERE 1=1"
                params = []
                if role == 'user':
                    query += " AND restaurant_id = %s"
                    params.append(restaurant_id_session)

                query += f" ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, params)
                menu = cursor.fetchall()
                flash("Menu items sorted successfully!", "success")

            return render_template('menu.html', menu=menu)

        elif action == 'clear':
            if 'filtered_menu' in session:
                session.pop('filtered_menu', None)

            query = "SELECT * FROM menu"
            params = []
            if role == 'user':
                query += " WHERE restaurant_id = %s"
                params.append(restaurant_id_session)

            cursor.execute(query, params)
            menu = cursor.fetchall()
            flash("All filters, sorting, and selections have been cleared.", "success")
            return render_template('menu.html', menu=menu)

    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('menu'))
