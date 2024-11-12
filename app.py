from flask import Flask, render_template,jsonify,request,redirect,url_for
from flask_cors import CORS
from Misc.conn import MongoDBConnector
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)

# MongoDB connection
db_connector = MongoDBConnector()
db_connector.connect()
client = db_connector.get_client()
db = client['HVpdf_Bot']
users_collection = db['Users']

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')


@app.route('/home')
def home():
    return "Welcome to the Home Page!"

##########################Login API ######################
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].lower()
    password = request.form['password']
    user = users_collection.find_one({'username': username.lower()})

    if not user:
        return jsonify({'error': 'Username does not exist'})

    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Incorrect password'})

    return redirect(url_for('home'))

#####################Sign UP##############################
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

########################Forgot Password lInk########################


if __name__ == '__main__':
    print('Backend is running!!!')
    app.run(host='0.0.0.0', port=5000, debug=True)