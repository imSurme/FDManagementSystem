from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')
    restaurant_id = session.get('restaurant_id')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('orders.html', orders=[])

    try:
        cursor = connection.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute('SELECT * FROM orders')
            orders = cursor.fetchall()
        elif role == 'user' and restaurant_id:
            cursor.execute('SELECT * FROM orders WHERE restaurant_id = %s', (restaurant_id,))
            orders = cursor.fetchall()
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        orders = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('orders.html', orders=orders)
    
def order_action():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    action = request.form.get('action')
    role = session.get('role')
    restaurant_id_session = session.get('restaurant_id') if role == 'user' else None

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('orders'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action == 'add':
            order_id = request.form.get('order_id')
            restaurant_id = request.form.get('restaurant_id')
            order_date = request.form.get('order_date')
            order_status = request.form.get('order_status')
            sales_qty = request.form.get('sales_qty')
            sales_amount = request.form.get('sales_amount')

            if role == 'user' and restaurant_id != str(restaurant_id_session):
                flash("Unauthorized action! You can only add order(s) for your restaurant.", "danger")
                return redirect(url_for('orders'))

            if not restaurant_id or not order_date or not order_status or not sales_qty or not sales_amount:
                flash("All fields are required (except Order ID).", "warning")
                return redirect(url_for('orders'))

            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone() #################################################

            if result['COUNT(*)'] == 0:
                flash('No restaurant found with that Restaurant ID!', 'danger')
                return redirect(url_for('orders'))

            if order_id:
                cursor.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
                existing_order = cursor.fetchone()

                if existing_order:
                    cursor.execute("SELECT order_id FROM orders")
                    used_ids = {row['order_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new Order ID is already in use. Please provide a unique ID. Suggestions: {suggestions}","warning")
                    return redirect(url_for('orders'))

                query = 'INSERT INTO orders (order_id, order_date, sales_qty, sales_amount, restaurant_id, order_status) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (order_id, order_date, sales_qty, sales_amount, restaurant_id, order_status))
            else:
                query = 'INSERT INTO orders (order_date, sales_qty, sales_amount, restaurant_id, order_status) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(query, (order_date, sales_qty, sales_amount, restaurant_id, order_status))
            connection.commit()
            flash("Order added successfully!", "success")

        elif action == 'delete':
            selected_ids = request.form.get('selected_orders')
            if not selected_ids:
                flash("No order(s) selected for deletion.", "warning")
                return redirect(url_for('orders'))

            selected_ids = selected_ids.split(',')

            if role == 'user':
                query = "DELETE FROM orders WHERE order_id IN ({}) AND restaurant_id = %s".format(','.join(['%s'] * len(selected_ids)))
                cursor.execute(query, selected_ids + [restaurant_id_session])
            else:
                query = "DELETE FROM orders WHERE order_id IN (%s)" % ','.join(['%s'] * len(selected_ids))
                cursor.execute(query, selected_ids)

            connection.commit()
            flash(f"Successfully deleted {cursor.rowcount} order(s).", "success")

        elif action == 'update':
            update_order_id = request.form.get('update_order_id')
            new_order_id = request.form.get('order_id')
            order_date = request.form.get('order_date')
            sales_qty = request.form.get('sales_qty')
            sales_amount = request.form.get('sales_amount')
            restaurant_id = request.form.get('restaurant_id')
            order_status = request.form.get('order_status')

            if not update_order_id:
                flash("No order selected for update.", "warning")
                return redirect(url_for('orders'))

            if role == 'user' and (restaurant_id != str(restaurant_id_session) or new_order_id != update_order_id):
                flash("Unauthorized action! You cannot change your Order's ID or Restaurant ID.", "danger")
                return redirect(url_for('orders'))

            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone()

            if result['COUNT(*)'] == 0:
                # If the Restaurant ID is not found, flash an error message
                flash('No restaurant found with that Restaurant ID!', 'danger')
                return redirect(url_for('orders'))

            if new_order_id != update_order_id:
                cursor.execute("SELECT COUNT(*) AS count FROM orders WHERE order_id = %s", (new_order_id,))
                result = cursor.fetchone()
                if result['count'] > 0:
                    cursor.execute("SELECT order_id FROM orders")
                    used_ids = {row['order_id'] for row in cursor.fetchall()}
                    all_possible_ids = set(range(1, 1001))
                    unused_ids = all_possible_ids - used_ids
                    suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                    flash(f"The new Order ID is already in use. Please provide a unique ID. Suggestions: {suggestions}","warning")
                    return redirect(url_for('orders'))

            query = "UPDATE orders SET order_id = %s, order_date = %s, sales_qty = %s, sales_amount = %s, restaurant_id = %s, order_status = %s WHERE order_id = %s"
            cursor.execute(query, (new_order_id, order_date, sales_qty, sales_amount, restaurant_id, order_status, update_order_id))
            connection.commit()
            flash("Order updated successfully!", "success")

        elif action == 'filter':
            order_id = request.form.get('order_id')
            order_date = request.form.get('order_date')
            sales_qty = request.form.get('sales_qty')
            sales_amount = request.form.get('sales_amount')
            restaurant_id = request.form.get('restaurant_id')
            order_status = request.form.get('order_status')

            if not any([order_id, order_date, sales_qty, sales_amount, restaurant_id, order_status]):
                flash("Please provide at least one filter criteria.", "warning")
                return redirect(url_for('orders'))

            query = "SELECT * FROM orders WHERE 1=1"
            params = []
            if role == 'user':
                query += " AND restaurant_id = %s"
                params.append(restaurant_id_session)

            if order_id:
                query += " AND order_id = %s"
                params.append(order_id)
            if order_date:
                query += " AND order_date = %s"
                params.append(order_date)
            if sales_qty:
                query += " AND sales_qty = %s"
                params.append(sales_qty)
            if sales_amount:
                query += " AND sales_amount = %s"
                params.append(sales_amount)
            if restaurant_id:
                query += " AND restaurant_id = %s"
                params.append(restaurant_id)
            if order_status:
                query += " AND order_status = %s"
                params.append(order_status)

            cursor.execute(query, params)
            orders = cursor.fetchall()
            session['filtered_orders'] = orders
            flash(f"Found {len(orders)} order(s) matching the criteria(s).", "success")
            return render_template('orders.html', orders=orders)

        elif action == 'sort':
            sort_by = request.form.get('sort_by')
            sort_order = request.form.get('sort_order')

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('orders'))

            if 'filtered_orders' in session and session['filtered_orders']:
                filtered_ids = [order['order_id'] for order in session['filtered_orders']]

                query = f"SELECT * FROM orders WHERE order_id IN ({','.join(['%s'] * len(filtered_ids))}) ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, filtered_ids)
                orders = cursor.fetchall()

                flash("Filtered orders sorted successfully!", "success")
            else:
                query = "SELECT * FROM orders WHERE 1=1"
                params = []
                if role == 'user':
                    query += " AND restaurant_id = %s"
                    params.append(restaurant_id_session)

                query += f" ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, params)
                orders = cursor.fetchall()
                flash("Orders sorted successfully!", "success")

            return render_template('orders.html', orders=orders)

        elif action == 'clear':
            if 'filtered_orders' in session:
                session.pop('filtered_orders', None)

            query = "SELECT * FROM orders"
            params = []
            if role == 'user':
                query += " WHERE restaurant_id = %s"
                params.append(restaurant_id_session)

            cursor.execute(query, params)
            orders = cursor.fetchall()
            flash("All filters, sorting, and selections have been cleared.", "success")
            return render_template('orders.html', orders=orders)
    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('orders'))
