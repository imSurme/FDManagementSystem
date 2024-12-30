from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def foods():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')
    restaurant_id = session.get('restaurant_id')

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('foods.html', foods=[])

    try:
        cursor = connection.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute('''
                SELECT f.food_id, f.item_name, f.veg_or_non_veg,
                       COUNT(m.menu_id) as menu_count
                FROM foods f
                LEFT JOIN menus m ON f.food_id = m.food_id
                GROUP BY f.food_id, f.item_name, f.veg_or_non_veg
            ''')
        elif role == 'user' and restaurant_id:
            cursor.execute('''
                SELECT DISTINCT f.food_id, f.item_name, f.veg_or_non_veg,
                       COUNT(m.menu_id) as menu_count
                FROM foods f
                LEFT JOIN menus m ON f.food_id = m.food_id
                WHERE m.restaurant_id = %s OR m.restaurant_id IS NULL
                GROUP BY f.food_id, f.item_name, f.veg_or_non_veg
            ''', (restaurant_id,))
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))

        foods_list = cursor.fetchall()
        return render_template('foods.html', foods=foods_list)

    except Error as e:
        print(f"Database error: {str(e)}")
        flash(f"Query failed: {e}", "danger")
        return render_template('foods.html', foods=[])
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def food_action():
    if 'logged_in' not in session:
        return redirect(url_for('foods'))

    action = request.form.get('action')
    connection = get_db_connection()
    
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('foods'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action == 'add':
            food_name = request.form.get('name')
            food_type = request.form.get('food_type')
            food_id = request.form.get('food_id')

            if not all([food_name, food_type]):
                flash("Food name and type are required.", "warning")
                return redirect(url_for('foods'))

            try:
                if food_id:
                    cursor.execute("SELECT food_id FROM foods WHERE food_id = %s", (food_id,))
                    if cursor.fetchone():
                        flash("Food ID already exists.", "warning")
                        return redirect(url_for('foods'))
                    
                    query = "INSERT INTO foods (food_id, item_name, veg_or_non_veg) VALUES (%s, %s, %s)"
                    cursor.execute(query, (food_id, food_name, food_type))
                else:
                    query = "INSERT INTO foods (item_name, veg_or_non_veg) VALUES (%s, %s)"
                    cursor.execute(query, (food_name, food_type))

                connection.commit()
                flash("Food item added successfully!", "success")

            except Error as e:
                connection.rollback()
                flash(f"Error adding food item: {str(e)}", "danger")

        elif action == 'delete':
            selected_ids = request.form.get('selected_food_items')
            
            if not selected_ids:
                flash("No food item(s) selected for deletion.", "warning")
                return redirect(url_for('foods'))

            selected_ids = selected_ids.split(',')
            
            try:
                query = "DELETE FROM foods WHERE food_id IN ({})".format(','.join(['%s'] * len(selected_ids)))
                cursor.execute(query, selected_ids)
                connection.commit()
                
                if cursor.rowcount > 0:
                    flash(f"Successfully deleted {cursor.rowcount} food item(s).", "success")
                else:
                    flash("No food items were deleted.", "warning")
                    
            except Error as e:
                flash(f"Error deleting food items: {str(e)}", "danger")
                connection.rollback()

        elif action == 'update':
            update_food_id = request.form.get('update_food_id')
            food_name = request.form.get('name')
            food_type = request.form.get('food_type')

            if not update_food_id:
                flash("No food item selected for update.", "warning")
                return redirect(url_for('foods'))

            try:
                query = """
                    UPDATE foods 
                    SET item_name = %s, veg_or_non_veg = %s
                    WHERE food_id = %s
                """
                cursor.execute(query, (food_name, food_type, update_food_id))
                connection.commit()
                flash("Food item updated successfully!", "success")

            except Error as e:
                connection.rollback()
                flash(f"Error updating food item: {str(e)}", "danger")

        elif action == 'filter':
            try:
                food_id = request.form.get('food_id')
                food_name = request.form.get('name')
                food_type = request.form.get('food_type')

                query = """
                    SELECT f.*, COUNT(m.menu_id) as menu_count
                    FROM foods f
                    LEFT JOIN menus m ON f.food_id = m.food_id
                    WHERE 1=1
                """
                params = []

                if food_id:
                    query += " AND f.food_id = %s"
                    params.append(food_id)
                if food_name:
                    query += " AND f.item_name LIKE %s"
                    params.append(f"%{food_name}%")
                if food_type:
                    query += " AND f.veg_or_non_veg = %s"
                    params.append(food_type)

                query += " GROUP BY f.food_id, f.item_name, f.veg_or_non_veg"
                cursor.execute(query, params)
                foods = cursor.fetchall()
                
                if foods:
                    flash(f"Found {len(foods)} food item(s) matching your criteria.", "success")
                else:
                    flash("No food items found matching your criteria.", "info")
                    
                return render_template('foods.html', foods=foods)

            except Error as e:
                flash(f"Error during filtering: {str(e)}", "danger")
                return redirect(url_for('foods'))

        elif action == 'sort':
            sort_by = request.form.get('sort_by')
            sort_order = request.form.get('sort_order')

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('foods'))

            query = f"""
                SELECT f.*, COUNT(m.menu_id) as menu_count
                FROM foods f
                LEFT JOIN menus m ON f.food_id = m.food_id
                GROUP BY f.food_id, f.item_name, f.veg_or_non_veg
                ORDER BY f.{sort_by} {sort_order}
            """
            cursor.execute(query)
            foods = cursor.fetchall()
            flash("Food items sorted successfully!", "success")
            return render_template('foods.html', foods=foods)

        elif action == 'clear':
            query = """
                SELECT f.*, COUNT(m.menu_id) as menu_count
                FROM foods f
                LEFT JOIN menus m ON f.food_id = m.food_id
                GROUP BY f.food_id, f.item_name, f.veg_or_non_veg
            """
            cursor.execute(query)
            foods = cursor.fetchall()
            flash("All filters and sorting have been cleared.", "success")
            return render_template('foods.html', foods=foods)

    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('foods')) 