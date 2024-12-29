from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from mysql.connector import Error

def restaurants():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    role = session.get('role')
    user_id = session.get('user_id') if role == 'user' else None

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return render_template('restaurants.html', restaurants=[], cities=[], restaurant_names=[], cuisines=[], clear_inputs={})

    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if there's an active filter in the session
        if 'active_filter' in session and session['active_filter']:
            # Use the stored filter parameters
            filter_params = session['filter_params']
            query = "SELECT * FROM restaurants WHERE 1=1"
            params = []
            
            if role == 'user':
                query += " AND user_id = %s"
                params.append(user_id)

            for key, value in filter_params.items():
                if value:
                    if key == 'restaurant_name' or key == 'city' or key == 'cuisine' or key == 'restaurant_address':
                        query += f" AND {key} LIKE %s"
                        params.append(f"%{value}%")
                    else:
                        query += f" AND {key} = %s"
                        params.append(value)

            cursor.execute(query, params)
            restaurants = cursor.fetchall()
        else:
            # Normal query without filters
            if role == 'admin':
                cursor.execute('SELECT * FROM restaurants')
                restaurants = cursor.fetchall()
            elif role == 'user' and user_id:
                cursor.execute('SELECT * FROM restaurants WHERE user_id = %s', (user_id,))
                restaurants = cursor.fetchall()

        cursor.execute('SELECT DISTINCT city FROM restaurants')
        cities = [row['city'] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT restaurant_name FROM restaurants')
        restaurant_names = [row['restaurant_name'] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT cuisine FROM restaurants')
        cuisines = [row['cuisine'] for row in cursor.fetchall()]
    except Error as e:
        flash(f"Query failed: {e}", "danger")
        restaurants = []
        cities = []
        restaurant_names = []
        cuisines = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    clear_inputs = {
        'restaurant_id': '',
        'user_id': '',
        'restaurant_name': '',
        'city': '',
        'rating': '',
        'rating_count': '',
        'average_cost': '',
        'cuisine': '',
        'restaurant_address': ''
    }

    return render_template('restaurants.html', restaurants=restaurants, cities=cities, restaurant_names=restaurant_names, cuisines=cuisines, clear_inputs=clear_inputs)

def restaurant_action():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    action = request.form.get('action')
    role = session.get('role')
    user_id = session.get('user_id') if role == 'user' else None
    restaurant_id_session = session.get('restaurant_id') if role == 'user' else None

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", "danger")
        return redirect(url_for('restaurants'))

    try:
        cursor = connection.cursor(dictionary=True)

        if action in ['add', 'update']:
            # Store current sort state before operation
            current_sort_by = request.form.get('last_sort_by') or session.get('last_sort_by')
            current_sort_order = request.form.get('last_sort_order') or session.get('last_sort_order')
            
            # Execute add/update operation
            if action == 'add':
                restaurant_id = request.form.get('restaurant_id')
                restaurant_name = request.form.get('restaurant_name')
                city = request.form.get('city')
                rating = request.form.get('rating') or None
                rating_count = request.form.get('rating_count')
                average_cost = request.form.get('average_cost')
                cuisine = request.form.get('cuisine')
                restaurant_address = request.form.get('restaurant_address')

                if not restaurant_name or not city or not average_cost or not cuisine or not restaurant_address:
                    flash("All fields are required (except Restaurant ID and Rating).", "warning")
                    return redirect(url_for('restaurants'))

                if role == 'user':
                    user_id = session['user_id']
                    cursor.execute("SELECT COUNT(*) FROM restaurants WHERE user_id = %s", (user_id,))
                    result = cursor.fetchone()
                    if result['COUNT(*)'] > 0:
                        flash("User can only have one restaurant.", "danger")
                        return redirect(url_for('restaurants'))
                else:
                    user_id = request.form.get('user_id')
                    cursor.execute("SELECT COUNT(*) FROM restaurants WHERE user_id = %s", (user_id,))
                    result = cursor.fetchone()
                    if result['COUNT(*)'] > 0:
                        flash("User can only have one restaurant.", "danger")
                        return redirect(url_for('restaurants'))

                if restaurant_id:
                    cursor.execute("SELECT restaurant_id FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
                    existing_restaurant = cursor.fetchone()

                    if existing_restaurant:
                        cursor.execute("SELECT restaurant_id FROM restaurants")
                        used_ids = {row['restaurant_id'] for row in cursor.fetchall()}
                        all_possible_ids = set(range(1, 1001))
                        unused_ids = all_possible_ids - used_ids
                        suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                        flash(f"The new Restaurant ID is already in use. Please provide a unique ID. Suggestions: {suggestions}", "warning")
                        return redirect(url_for('restaurants'))

                    query = 'INSERT INTO restaurants (restaurant_id, user_id, restaurant_name, city, rating, rating_count, average_cost, cuisine, restaurant_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    cursor.execute(query, (restaurant_id, user_id, restaurant_name, city, rating, rating_count, average_cost, cuisine, restaurant_address))
                else:
                    query = 'INSERT INTO restaurants (user_id, restaurant_name, city, rating, rating_count, average_cost, cuisine, restaurant_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                    cursor.execute(query, (user_id, restaurant_name, city, rating, rating_count, average_cost, cuisine, restaurant_address))
                connection.commit()
                flash("Restaurant added successfully!", "success")

            elif action == 'update':
                update_restaurant_id = request.form.get('update_restaurant_id')
                new_restaurant_id = request.form.get('restaurant_id')
                restaurant_name = request.form.get('restaurant_name')
                city = request.form.get('city')
                rating = request.form.get('rating') or None
                rating_count = request.form.get('rating_count')
                average_cost = request.form.get('average_cost')
                cuisine = request.form.get('cuisine')
                restaurant_address = request.form.get('restaurant_address')

                if not update_restaurant_id:
                    flash("No restaurant selected for update.", "warning")
                    return redirect(url_for('restaurants'))

                if role == 'user':
                    cursor.execute("SELECT user_id FROM restaurants WHERE restaurant_id = %s", (update_restaurant_id,))
                    result = cursor.fetchone()
                    if result['user_id'] != user_id:
                        flash("Unauthorized action! You can only update your own restaurant.", "danger")
                        return redirect(url_for('restaurants'))

                if new_restaurant_id != update_restaurant_id:
                    cursor.execute("SELECT COUNT(*) AS count FROM restaurants WHERE restaurant_id = %s", (new_restaurant_id,))
                    result = cursor.fetchone()
                    if result['count'] > 0:
                        cursor.execute("SELECT restaurant_id FROM restaurants")
                        used_ids = {row['restaurant_id'] for row in cursor.fetchall()}
                        all_possible_ids = set(range(1, 1001))
                        unused_ids = all_possible_ids - used_ids
                        suggestions = ', '.join(map(str, sorted(unused_ids)[:3]))
                        flash(f"The new Restaurant ID is already in use. Please provide a unique ID. Suggestions: {suggestions}", "warning")
                        return redirect(url_for('restaurants'))

                query = "UPDATE restaurants SET restaurant_id = %s, restaurant_name = %s, city = %s, rating = %s, rating_count = %s, average_cost = %s, cuisine = %s, restaurant_address = %s WHERE restaurant_id = %s"
                cursor.execute(query, (new_restaurant_id, restaurant_name, city, rating, rating_count, average_cost, cuisine, restaurant_address, update_restaurant_id))
                connection.commit()

                if 'filtered_restaurants' in session:
                    filtered_restaurants = session['filtered_restaurants']
                    filtered_ids = [restaurant['restaurant_id'] for restaurant in filtered_restaurants]
                    query = f"SELECT * FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})"
                    cursor.execute(query, filtered_ids)
                    restaurants = cursor.fetchall()
                    flash("Restaurant updated successfully!", "success")
                    return render_template('restaurants.html', restaurants=restaurants, cities=[], restaurant_names=[], cuisines=[], clear_inputs={})
                else:
                    flash("Restaurant updated successfully!", "success")

            # After successful operation, reapply sort if it exists
            if current_sort_by and current_sort_order:
                query = "SELECT * FROM restaurants WHERE 1=1"
                params = []
                if role == 'user':
                    query += " AND user_id = %s"
                    params.append(user_id)
                
                query += f" ORDER BY {current_sort_by} {current_sort_order}"
                cursor.execute(query, params)
                restaurants = cursor.fetchall()
                
                return render_template('restaurants.html', restaurants=restaurants, cities=[], restaurant_names=[], cuisines=[], clear_inputs={})

            # After successful operation, check if we need to reapply filter or sort
            if 'filtered_restaurants' in session:
                # Reapply filter
                return redirect(url_for('restaurant_action', action='filter'))
            elif 'last_sort_by' in session and 'last_sort_order' in session:
                # Reapply sort
                return redirect(url_for('restaurant_action', action='sort'))

        elif action == 'delete':
            # Store current sort state before operation
            current_sort_by = request.form.get('last_sort_by') or session.get('last_sort_by')
            current_sort_order = request.form.get('last_sort_order') or session.get('last_sort_order')

            selected_ids = request.form.get('selected_restaurants')
            if not selected_ids:
                flash("No restaurant(s) selected for deletion.", "warning")
                return redirect(url_for('restaurants'))

            selected_ids = selected_ids.split(',')

            if role == 'user':
                if any(restaurant_id != str(restaurant_id_session) for restaurant_id in selected_ids):
                    flash("Unauthorized action! You can only delete your own restaurant.", "danger")
                    return redirect(url_for('restaurants'))
                query = "DELETE FROM restaurants WHERE restaurant_id IN ({}) AND user_id = %s".format(','.join(['%s'] * len(selected_ids)))
                cursor.execute(query, selected_ids + [user_id])
            else:
                query = "DELETE FROM restaurants WHERE restaurant_id IN (%s)" % ','.join(['%s'] * len(selected_ids))
                cursor.execute(query, selected_ids)

            connection.commit()
            flash(f"Successfully deleted {cursor.rowcount} restaurant(s).", "success")

            # After successful delete, reapply sort if it exists
            if current_sort_by and current_sort_order:
                query = "SELECT * FROM restaurants WHERE 1=1"
                params = []
                if role == 'user':
                    query += " AND user_id = %s"
                    params.append(user_id)
                
                query += f" ORDER BY {current_sort_by} {current_sort_order}"
                cursor.execute(query, params)
                restaurants = cursor.fetchall()
                
                return render_template('restaurants.html', restaurants=restaurants, cities=[], restaurant_names=[], cuisines=[], clear_inputs={})

        elif action == 'filter':
            # Store filter parameters in session
            session['filter_params'] = {
                'restaurant_id': request.form.get('restaurant_id'),
                'user_id': request.form.get('user_id'),
                'restaurant_name': request.form.get('restaurant_name'),
                'city': request.form.get('city'),
                'rating': request.form.get('rating'),
                'rating_count': request.form.get('rating_count'),
                'average_cost': request.form.get('average_cost'),
                'cuisine': request.form.get('cuisine'),
                'restaurant_address': request.form.get('restaurant_address')
            }
            session['active_filter'] = True

            restaurant_id = request.form.get('restaurant_id')
            user_id = request.form.get('user_id')
            restaurant_name = request.form.get('restaurant_name')
            city = request.form.get('city')
            rating = request.form.get('rating')
            rating_count = request.form.get('rating_count')
            average_cost = request.form.get('average_cost')
            cuisine = request.form.get('cuisine')
            restaurant_address = request.form.get('restaurant_address')

            if not any([restaurant_id, user_id, restaurant_name, city, rating, rating_count, average_cost, cuisine, restaurant_address]):
                flash("Please provide at least one filter criteria.", "warning")
                return redirect(url_for('restaurants'))

            query = "SELECT * FROM restaurants WHERE 1=1"
            params = []
            if role == 'user':
                query += " AND user_id = %s"
                params.append(user_id)

            if restaurant_id:
                query += " AND restaurant_id = %s"
                params.append(restaurant_id)
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            if restaurant_name:
                query += " AND restaurant_name LIKE %s"
                params.append(f"%{restaurant_name}%")
            if city:
                query += " AND city LIKE %s"
                params.append(f"%{city}%")
            if rating:
                if rating == '0':
                    query += " AND rating IS NULL"
                elif rating.endswith('+'):
                    query += " AND rating >= %s"
                    params.append(float(rating[:-1]))
                else:
                    query += " AND rating = %s"
                    params.append(rating)
            if rating_count:
                query += " AND rating_count = %s"
                params.append(rating_count)
            if average_cost:
                query += " AND average_cost = %s"
                params.append(average_cost)
            if cuisine:
                query += " AND cuisine LIKE %s"
                params.append(f"%{cuisine}%")
            if restaurant_address:
                query += " AND restaurant_address LIKE %s"
                params.append(f"%{restaurant_address}%")

            cursor.execute(query, params)
            restaurants = cursor.fetchall()
            session['filtered_restaurants'] = restaurants

            if not restaurants:
                flash("No restaurants found matching the criteria.", "warning")
                return render_template('restaurants.html', restaurants=[], cities=[], restaurant_names=[], cuisines=[], clear_inputs={})

            # Update the lists based on the filtered data
            filtered_ids = [restaurant['restaurant_id'] for restaurant in restaurants]
            if filtered_ids:
                cursor.execute(f"SELECT DISTINCT city FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})", filtered_ids)
                cities = [row['city'] for row in cursor.fetchall()]
                cursor.execute(f"SELECT DISTINCT restaurant_name FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})", filtered_ids)
                restaurant_names = [row['restaurant_name'] for row in cursor.fetchall()]
                cursor.execute(f"SELECT DISTINCT cuisine FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})", filtered_ids)
                cuisines = [row['cuisine'] for row in cursor.fetchall()]
            else:
                cities = []
                restaurant_names = []
                cuisines = []

            # Pass the input values back to the template
            clear_inputs = {
                'restaurant_id': restaurant_id,
                'user_id': user_id,
                'restaurant_name': restaurant_name,
                'city': city,
                'rating': rating,
                'rating_count': rating_count,
                'average_cost': average_cost,
                'cuisine': cuisine,
                'restaurant_address': restaurant_address
            }

            flash(f"Found {len(restaurants)} restaurant(s) matching the criteria(s).", "success")
            return render_template('restaurants.html', restaurants=restaurants, cities=cities, restaurant_names=restaurant_names, cuisines=cuisines, clear_inputs=clear_inputs)

        elif action == 'sort':
            sort_by = request.form.get('sort_by') or session.get('last_sort_by')
            sort_order = request.form.get('sort_order') or session.get('last_sort_order')

            # Store sort parameters in session
            session['last_sort_by'] = sort_by
            session['last_sort_order'] = sort_order

            if not sort_by or sort_order not in ['ASC', 'DESC']:
                flash("Invalid sort parameters.", "danger")
                return redirect(url_for('restaurants'))

            if 'filtered_restaurants' in session and session['filtered_restaurants']:
                filtered_ids = [restaurant['restaurant_id'] for restaurant in session['filtered_restaurants']]
                if filtered_ids:
                    query = f"SELECT * FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))}) ORDER BY {sort_by} {sort_order}"
                    cursor.execute(query, filtered_ids)
                    restaurants = cursor.fetchall()
                    flash("Restaurants sorted successfully!", "success")
                else:
                    restaurants = []
            else:
                query = "SELECT * FROM restaurants WHERE 1=1"
                params = []
                if role == 'user':
                    query += " AND user_id = %s"
                    params.append(user_id)

                query += f" ORDER BY {sort_by} {sort_order}"
                cursor.execute(query, params)
                restaurants = cursor.fetchall()
                flash("Restaurants sorted successfully!", "success")

            if not restaurants:
                flash("No restaurants found to sort.", "warning")
                return render_template('restaurants.html', restaurants=[], cities=[], restaurant_names=[], cuisines=[], clear_inputs={})

            # Update the lists based on the sorted data
            filtered_ids = [restaurant['restaurant_id'] for restaurant in restaurants]
            if filtered_ids:
                cursor.execute(f"SELECT DISTINCT city FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})", filtered_ids)
                cities = [row['city'] for row in cursor.fetchall()]
                cursor.execute(f"SELECT DISTINCT restaurant_name FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})", filtered_ids)
                restaurant_names = [row['restaurant_name'] for row in cursor.fetchall()]
                cursor.execute(f"SELECT DISTINCT cuisine FROM restaurants WHERE restaurant_id IN ({','.join(['%s'] * len(filtered_ids))})", filtered_ids)
                cuisines = [row['cuisine'] for row in cursor.fetchall()]
            else:
                cities = []
                restaurant_names = []
                cuisines = []

            # Clear form inputs
            clear_inputs = {
                'restaurant_id': '',
                'user_id': '',
                'restaurant_name': '',
                'city': '',
                'rating': '',
                'rating_count': '',
                'average_cost': '',
                'cuisine': '',
                'restaurant_address': ''
            }

            return render_template('restaurants.html', restaurants=restaurants, cities=cities, restaurant_names=restaurant_names, cuisines=cuisines, clear_inputs=clear_inputs)

        elif action == 'clear':
            # Clear all stored states
            for key in ['filtered_restaurants', 'last_sort_by', 'last_sort_order', 'filter_params', 'active_filter']:
                if key in session:
                    session.pop(key)

            # If this is an unload clear request, just clear session and return
            if request.form.get('clear_filter') == 'true':
                return '', 204  # Return empty response

            # Normal clear operation
            query = "SELECT * FROM restaurants"
            params = []
            if role == 'user':
                query += " WHERE user_id = %s"
                params.append(user_id)

            cursor.execute(query, params)
            restaurants = cursor.fetchall()

            # Get fresh lists
            cursor.execute('SELECT DISTINCT city FROM restaurants')
            cities = [row['city'] for row in cursor.fetchall()]
            cursor.execute('SELECT DISTINCT restaurant_name FROM restaurants')
            restaurant_names = [row['restaurant_name'] for row in cursor.fetchall()]
            cursor.execute('SELECT DISTINCT cuisine FROM restaurants')
            cuisines = [row['cuisine'] for row in cursor.fetchall()]

            clear_inputs = {
                'restaurant_id': '',
                'user_id': '',
                'restaurant_name': '',
                'city': '',
                'rating': '',
                'rating_count': '',
                'average_cost': '',
                'cuisine': '',
                'restaurant_address': ''
            }

            flash("All filters, sorting, and selections have been cleared.", "success")
            return render_template('restaurants.html', 
                                restaurants=restaurants, 
                                cities=cities, 
                                restaurant_names=restaurant_names, 
                                cuisines=cuisines, 
                                clear_inputs=clear_inputs)

    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('restaurants'))
