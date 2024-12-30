from flask import Flask
from flask_session import Session
from index import index
from auth import login, logout
from users import users, user_action
from restaurants import restaurants, restaurant_action
from couriers import couriers, courier_action
from menus import menus, menus_action
from orders import orders, order_action
from foods import foods, food_action

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'a_secret_key'
Session(app)

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/users', 'users', users)
app.add_url_rule('/users', 'user_action', user_action, methods=['POST'])
app.add_url_rule('/restaurants', 'restaurants', restaurants)
app.add_url_rule('/restaurants', 'restaurant_action', restaurant_action, methods=['POST'])
app.add_url_rule('/couriers', 'couriers', couriers)
app.add_url_rule('/couriers', 'courier_action', courier_action, methods=['POST'])
app.add_url_rule('/menus', 'menus', menus)
app.add_url_rule('/menus', 'menus_action', menus_action, methods=['POST'])
app.add_url_rule('/orders', 'orders', orders)
app.add_url_rule('/orders', 'order_action', order_action, methods=['POST'])
app.add_url_rule('/foods', 'foods', foods)
app.add_url_rule('/foods', 'food_action', food_action, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
