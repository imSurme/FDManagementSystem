from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def menus():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')
    restaurant_id = session.get('restaurant_id')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('menus.html', menus=[])

    try:
        cursor = connection.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute('''
                SELECT m.menu_id, m.restaurant_id, m.food_id, m.cuisine, m.price,
                       f.item_name as food_name, f.veg_or_non_veg 
                FROM menus m 
                LEFT JOIN foods f ON m.food_id = f.food_id
            ''')
        elif role == 'user' and restaurant_id:
            cursor.execute('''
                SELECT m.menu_id, m.restaurant_id, m.food_id, m.cuisine, m.price,
                       f.item_name as food_name, f.veg_or_non_veg 
                FROM menus m 
                LEFT JOIN foods f ON m.food_id = f.food_id 
                WHERE m.restaurant_id = %s
            ''', (restaurant_id,))
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))

        menus_list = cursor.fetchall()
        print("Fetched menus:", menus_list)  # Debug print
        return render_template('menus.html', menus=menus_list)

    except Error as e:
        print(f"Database error: {str(e)}")  # Debug print
        flash(f"Query failed: {e}", "danger")
        return render_template('menus.html', menus=[])
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def menus_action():
    if 'logged_in' not in session:
        return redirect(url_for('menus'))

    action = request.form.get('action')
    role = session.get('role')
    restaurant_id_session = session.get('restaurant_id') if role == 'user' else None

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('menus'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action == 'add':
            # Get form data
            food_name = request.form.get('name')
            food_type = request.form.get('food_type')
            cuisine = request.form.get('cuisine')
            price = request.form.get('price')
            restaurant_id = request.form.get('restaurant_id')
            menu_id = request.form.get('menu_id')  # Changed from menus_id

            # Validate required fields
            if not all([food_name, food_type, cuisine, price, restaurant_id]):
                flash("All fields are required except Menu ID.", "warning")
                return redirect(url_for('menus'))

            try:
                # Check if restaurant exists
                cursor.execute("SELECT COUNT(*) as count FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
                result = cursor.fetchone()
                if result['count'] == 0:
                    flash('No restaurant found with that Restaurant ID!', 'danger')
                    return redirect(url_for('menus'))

                # First, insert or get the food item
                cursor.execute("""
                    SELECT food_id FROM foods 
                    WHERE item_name = %s AND veg_or_non_veg = %s
                """, (food_name, food_type))
                food_result = cursor.fetchone()

                if not food_result:
                    # Create new food item
                    cursor.execute("""
                        INSERT INTO foods (item_name, veg_or_non_veg)
                        VALUES (%s, %s)
                    """, (food_name, food_type))
                    food_id = cursor.lastrowid
                else:
                    food_id = food_result['food_id']

                # Then insert the menu item
                if menu_id:
                    # Check if menu_id already exists
                    cursor.execute("SELECT menu_id FROM menus WHERE menu_id = %s", (menu_id,))
                    if cursor.fetchone():
                        flash("Menu ID already exists. Please use a different ID.", "warning")
                        return redirect(url_for('menus'))
                    
                    query = """
                        INSERT INTO menus (menu_id, restaurant_id, food_id, cuisine, price) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (menu_id, restaurant_id, food_id, cuisine, price))
                else:
                    query = """
                        INSERT INTO menus (restaurant_id, food_id, cuisine, price) 
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query, (restaurant_id, food_id, cuisine, price))

                connection.commit()
                flash("Menu item added successfully!", "success")

            except Error as e:
                print(f"Database error: {str(e)}")  # Debug print
                connection.rollback()
                flash(f"Error adding menu item: {str(e)}", "danger")

        elif action == 'delete':
            selected_ids = request.form.get('selected_menu_items')
            print("Form data received:", request.form)  # Debug print
            print("Selected IDs received:", selected_ids)  # Debug print
            
            if not selected_ids:
                flash("No menu item(s) selected for deletion.", "warning")
                return redirect(url_for('menus'))

            selected_ids = selected_ids.split(',')
            print("Selected IDs after split:", selected_ids)  # Debug print
            
            try:
                if role == 'user':
                    query = "DELETE FROM menus WHERE menu_id IN ({}) AND restaurant_id = %s".format(','.join(['%s'] * len(selected_ids)))
                    params = selected_ids + [restaurant_id_session]
                else:
                    query = "DELETE FROM menus WHERE menu_id IN ({})".format(','.join(['%s'] * len(selected_ids)))
                    params = selected_ids

                print("Query:", query)  # Debug print
                print("Parameters:", params)  # Debug print
                
                cursor.execute(query, params)
                connection.commit()
                
                print("Rows affected:", cursor.rowcount)  # Debug print
                
                if cursor.rowcount > 0:
                    flash(f"Successfully deleted {cursor.rowcount} menu item(s).", "success")
                else:
                    flash("No menu items were deleted. Please check your permissions.", "warning")
                    
            except Error as e:
                print(f"Database error: {str(e)}")
                flash(f"Error deleting menu items: {str(e)}", "danger")
                connection.rollback()

            return redirect(url_for('menus'))

        elif action == 'update':
            update_menu_id = request.form.get('update_menu_id')
            food_name = request.form.get('name')
            food_type = request.form.get('food_type')
            cuisine = request.form.get('cuisine')
            price = request.form.get('price')
            restaurant_id = request.form.get('restaurant_id')

            # Add debug logging
            print("Update request received with data:", {
                'update_menu_id': update_menu_id,
                'food_name': food_name,
                'food_type': food_type,
                'cuisine': cuisine,
                'price': price,
                'restaurant_id': restaurant_id
            })

            if not update_menu_id:
                flash("No menu item selected for update.", "warning")
                return redirect(url_for('menus'))

            try:
                # First, get the food_id based on the food name and type
                cursor.execute("""
                    SELECT food_id FROM foods 
                    WHERE item_name = %s AND veg_or_non_veg = %s
                """, (food_name, food_type))
                food_result = cursor.fetchone()
                
                print("Food query result:", food_result)  # Debug log
                
                if not food_result:
                    # If food doesn't exist, create it
                    cursor.execute("""
                        INSERT INTO foods (item_name, veg_or_non_veg)
                        VALUES (%s, %s)
                    """, (food_name, food_type))
                    food_id = cursor.lastrowid
                    print("Created new food with ID:", food_id)  # Debug log
                else:
                    food_id = food_result['food_id']
                    print("Found existing food with ID:", food_id)  # Debug log

                # Now update the menu item
                query = """
                    UPDATE menus 
                    SET food_id = %s, cuisine = %s, price = %s, restaurant_id = %s 
                    WHERE menu_id = %s
                """
                params = (food_id, cuisine, price, restaurant_id, update_menu_id)
                print("Update query:", query)  # Debug log
                print("Update parameters:", params)  # Debug log
                
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
                print("Rows affected by update:", rows_affected)  # Debug log
                
                connection.commit()
                flash("Menu item updated successfully!", "success")

            except Error as e:
                print("Database error:", str(e))  # Debug log
                connection.rollback()
                flash(f"Error updating menu item: {str(e)}", "danger")
                return redirect(url_for('menus'))

        elif action == 'filter':
            try:
                menu_id = request.form.get('menu_id')
                food_name = request.form.get('name')
                food_type = request.form.get('food_type')
                cuisine = request.form.get('cuisine')
                price = request.form.get('price')
                restaurant_id = request.form.get('restaurant_id')

                query = """
                    SELECT m.menu_id, m.restaurant_id, m.cuisine, m.price,
                           f.item_name as food_name, f.veg_or_non_veg 
                    FROM menus m 
                    LEFT JOIN foods f ON m.food_id = f.food_id 
                    WHERE 1=1
                """
                params = []

                # Add conditions based on user role
                if role == 'user':
                    query += " AND m.restaurant_id = %s"
                    params.append(restaurant_id_session)

                # Add filter conditions
                if menu_id:
                    query += " AND m.menu_id = %s"
                    params.append(menu_id)
                if food_name:
                    query += " AND f.item_name LIKE %s"
                    params.append(f"%{food_name}%")
                if food_type:
                    query += " AND f.veg_or_non_veg = %s"
                    params.append(food_type)
                if cuisine:
                    query += " AND m.cuisine LIKE %s"
                    params.append(f"%{cuisine}%")
                if price:
                    query += " AND m.price = %s"
                    params.append(price)
                if restaurant_id:
                    query += " AND m.restaurant_id = %s"
                    params.append(restaurant_id)

                cursor.execute(query, params)
                menus = cursor.fetchall()
                
                if menus:
                    flash(f"Found {len(menus)} menu item(s) matching your criteria.", "success")
                else:
                    flash("No menu items found matching your criteria.", "info")
                    
                return render_template('menus.html', menus=menus)

            except Error as e:
                flash(f"Error during filtering: {str(e)}", "danger")
                return redirect(url_for('menus'))

        elif action == 'sort':
            sort_by = request.form.get('sort_by')
            sort_order = request.form.get('sort_order')

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('menus'))

            # Modify the sort_by column for special cases
            order_clause = ""
            if sort_by == 'item_name':
                order_clause = f"f.item_name {sort_order}"
            elif sort_by == 'veg_or_non_veg':
                order_clause = f"f.veg_or_non_veg {sort_order}"
            else:
                order_clause = f"m.{sort_by} {sort_order}"

            if 'filtered_menus' in session and session['filtered_menus']:
                filtered_ids = [item['menus_id'] for item in session['filtered_menus']]

                query = f"""
                    SELECT m.*, f.item_name as food_name, f.veg_or_non_veg 
                    FROM menus m 
                    LEFT JOIN foods f ON m.food_id = f.food_id 
                    WHERE m.menus_id IN ({','.join(['%s'] * len(filtered_ids))}) 
                    ORDER BY {order_clause}
                """
                cursor.execute(query, filtered_ids)
                menus = cursor.fetchall()

                # Transform the menus items to use food_name when available
                for item in menus:
                    if item['food_name']:
                        item['name'] = item['food_name']

                flash("Filtered menus items sorted successfully!", "success")
            else:
                query = """
                    SELECT m.*, f.item_name as food_name, f.veg_or_non_veg 
                    FROM menus m 
                    LEFT JOIN foods f ON m.food_id = f.food_id 
                    WHERE 1=1
                """
                params = []
                if role == 'user':
                    query += " AND m.restaurant_id = %s"
                    params.append(restaurant_id_session)

                query += f" ORDER BY {order_clause}"
                cursor.execute(query, params)
                menus = cursor.fetchall()

                # Transform the menus items to use food_name when available
                for item in menus:
                    if item['food_name']:
                        item['name'] = item['food_name']

                flash("menus items sorted successfully!", "success")

            return render_template('menus.html', menus=menus)

        elif action == 'clear':
            if 'filtered_menus' in session:
                session.pop('filtered_menus', None)

            # Update the query to include JOIN with foods table
            query = """
                SELECT m.*, f.item_name as food_name, f.veg_or_non_veg 
                FROM menus m 
                LEFT JOIN foods f ON m.food_id = f.food_id 
                WHERE 1=1
            """
            params = []
            if role == 'user':
                query += " AND m.restaurant_id = %s"
                params.append(restaurant_id_session)

            cursor.execute(query, params)
            menus = cursor.fetchall()

            # Transform the menus items to use food_name when available
            for item in menus:
                if item['food_name']:
                    item['name'] = item['food_name']

            flash("All filters, sorting, and selections have been cleared.", "success")
            return render_template('menus.html', menus=menus)

    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('menus'))
