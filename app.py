from flask import Flask, render_template,jsonify,request,redirect,url_for
from flask_cors import CORS
from Misc.conn import MongoDBConnector
from Misc.session import SessionManager
from werkzeug.security import check_password_hash, generate_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("Secret_Key")
CORS(app)

##################### Initialize Session ####################

session_manager = SessionManager()

###################### MongoDB connection ###################

db_connector = MongoDBConnector()
db_connector.connect()
client = db_connector.get_client()
db = client['HVpdf_Bot']
users_collection = db['Users']

####################### Login ##########################

@app.route('/', methods=['GET'])
def index():
    if session_manager.is_user_logged_in():
        return redirect(url_for('home'))
    return render_template('login.html')

####################### Login ##########################

@app.route('/about')
def about():
    return render_template('AboutUs.html')

########################## HVPDF Chat Home ########################

@app.route('/home')
def home():
    redirect_response = session_manager.redirect_if_not_logged_in()
    if redirect_response:
        return redirect_response
    username = session_manager.get_logged_in_user()
    return render_template('home.html', username=username)

########################## Login API ######################

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].lower()
    password = request.form['password']
    user = users_collection.find_one({'username': username.lower()})

    if not user:
        return jsonify({'error': 'Username does not exist'})

    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Incorrect password'})
    
    session_manager.set_user_session(username)

    return redirect(url_for('home'))

######################### Sign UP ##########################

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already exists'})

    hashed_password = generate_password_hash(password)
    new_user = {
        'username': username,
        'password': hashed_password,
        'email': email
    }
    users_collection.insert_one(new_user)
    return jsonify({'success': 'User registered successfully'})

######################## Forgot Password link ########################


######################## Logout #############################

@app.route('/logout')
def logout():
    session_manager.clear_user_session()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print('Backend is running!!!')
    app.run(host='0.0.0.0', port=5000, debug=True)