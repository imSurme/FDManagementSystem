from flask import Flask
from flask_session import Session
from index import index
from auth import login, logout
from restaurants import restaurants, restaurant_action
from couriers import couriers, courier_action
from menu import menu, menu_action
from orders import orders, order_action

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'a_secret_key'
Session(app)

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/restaurants', 'restaurants', restaurants)
app.add_url_rule('/restaurants', 'restaurant_action', restaurant_action, methods=['POST'])
app.add_url_rule('/couriers', 'couriers', couriers)
app.add_url_rule('/couriers', 'courier_action', courier_action, methods=['POST'])
app.add_url_rule('/menu', 'menu', menu)
app.add_url_rule('/menu', 'menu_action', menu_action, methods=['POST'])
app.add_url_rule('/orders', 'orders', orders)
app.add_url_rule('/orders', 'order_action', order_action, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
