from flask import Flask
from flask_session import Session
from index import index
from auth import login, logout
from restaurants import restaurants
from couriers import couriers, courier_action

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'a_secret_key'
Session(app)

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/restaurants', 'restaurants', restaurants)
app.add_url_rule('/couriers', 'couriers', couriers)
app.add_url_rule('/couriers', 'courier_action', courier_action, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
