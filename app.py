import os
import io
import asyncio
import uuid
import json
from datetime import datetime, timezone
import stripe
from flask import Flask, render_template,jsonify,request,redirect,url_for
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from Misc.conn import MongoDBConnector
from Misc.session import SessionManager
from ML_Models.pdf_extractor import PDFExtractor
from ML_Models.ML_Logic import QueryBot
from Subscriptions.pricing import PricingValidator

app = Flask(__name__)
app.secret_key = os.getenv("Secret_Key")
base_directory = os.getenv("Base_Dir")
stripe.api_key = os.getenv("STRIPE_KEY")
CORS(app)

##################### Initialize Session ####################

session_manager = SessionManager()

###################### MongoDB connection ###################

db_connector = MongoDBConnector()
db_connector.connect()
client = db_connector.get_client()
db = client['HVpdf_Bot']
users_collection = db['Users']
vector_collection = db['User_Vectors']
chat_collection = db['User_Chats']

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

####################### Pricing ##########################

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

####################### Pricing ##########################

@app.route('/contact')
def contact():
    return render_template('contact.html')

########################## HVPDF Chat Home ########################

@app.route('/home')
def home():
    redirect_response = session_manager.redirect_if_not_logged_in()
    if redirect_response:
        return redirect_response
    username = session_manager.get_logged_in_user()
    user = users_collection.find_one({"username": username})
    if not user:
        session_manager.clear_user_session()
        return redirect(url_for('index'))
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
        'email': email,
        "created_at": datetime.now(timezone.utc),
        'plan': 'Free'
    }
    users_collection.insert_one(new_user)
    return jsonify({'success': 'User registered successfully'})

######################## Forgot Password link ########################


######################## Uploaded Files Validation Based On Subscription #######################

@app.route('/validate_files', methods=['POST'])
def validate_files():
    files = request.files.getlist('files[]')
    username = session_manager.get_logged_in_user()
    user_data = users_collection.find_one({"username": username})
    subscription_type = user_data.get("plan")

    validator = PricingValidator(subscription_type)

    is_valid, error_message = validator.validate_file_count(len(files))
    if not is_valid:
        return jsonify({"error": error_message}), 400

    extractor = PDFExtractor()
    results = []

    for file in files:
        file_status = {"filename": file.filename}
        is_valid, error_message = validator.validate_file_size(file)
        
        if not is_valid:
            file_status["status"] = error_message
            results.append(file_status)
            continue
        
        if not file.filename.endswith('.pdf'):
            file_status["status"] = "❌ File extension is incorrect"
            results.append(file_status)
            continue
        
        file.seek(0)
        is_valid, error_message = validator.validate_page_count(io.BytesIO(file.read()))
        
        if not is_valid:
            file_status["status"] = error_message
            results.append(file_status)
            continue

        try:
            file.seek(0)
            file_stream = io.BytesIO(file.read())
            extracted_text = asyncio.run(extractor._extract_text_from_pdf(file_stream))
            if extracted_text.strip():
                file_status["status"] = "✅ Text extracted successfully"
            else:
                file_status["status"] = "❌ No text extracted. File may be corrupted."
        except Exception as e:
            file_status["status"] = f"❌ {str(e)}"

        results.append(file_status)

    return jsonify({"results": results})


######################## Process Files #########################################

@app.route('/process_files', methods=['POST'])
def process_files():
    files = request.files.getlist('files[]')
    username = session_manager.get_logged_in_user()
    if not files:
        return jsonify({"error": "No files uploaded"}), 400
    
    extractor = PDFExtractor()
    session_id = str(uuid.uuid4())
    save_directory = os.path.join(base_directory, username)
    os.makedirs(save_directory, exist_ok=True)
    faiss_index_path = os.path.join(save_directory, session_id)

    try:
        file_streams = [io.BytesIO(file.read()) for file in files]
        raw_text = asyncio.run(extractor.extract_text(file_streams))
        text_chunks = extractor.chunk_text(raw_text)
        vector_store = extractor.create_vector_store(text_chunks)
        vector_store.save_local(faiss_index_path)

        vector_data = {
            "username": username,
            "session_id": session_id,
            "faiss_index_path": faiss_index_path
        }

        vector_collection.insert_one(vector_data)
        session_url = f"/c/{session_id}"
        return jsonify({"session_url": session_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

######################## Open a new session ###############################

@app.route('/home', defaults={'session_id': None})
@app.route('/c/<session_id>')
def session_home(session_id):
    username = session_manager.get_logged_in_user()
    session_data = vector_collection.find_one({"session_id": session_id})
    sessions = list(chat_collection.find({"username": username}))

    if not sessions:
        session_titles = []
    else:
        session_titles = [
            {"title": session["title"], 
             "session_id": session["session_id"],
             "date": session["created_at"].replace(tzinfo=timezone.utc).astimezone(timezone.utc).strftime('%Y-%m-%d')}
            for session in sessions
        ]

    print(session_titles)

    messages = []
    if sessions:
        for session in sessions:
            session_messages = session.get("messages", [])
            messages.extend(session_messages)

    if not session_data:
        return "Session not found", 404

    return render_template(
        'home_chat.html', 
        session_id=session_id, 
        username=username,
        session_titles=json.dumps(session_titles),
        messages=json.dumps(messages))

######################### Making conversations ############################

@app.route('/query-bot', methods=['POST'])
async def query_bot():
    try:
        data = request.json        
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        session_id = data.get('session_id')
        user_question = data.get('question')
        username = data.get('username')

        user_data = users_collection.find_one({"username": username})
        subscription_type = user_data.get("plan")
        
        if not session_id or not user_question:
            return jsonify({"error": "Missing session_id or question"}), 400
        
        session_data = vector_collection.find_one({"session_id": session_id})
        
        if not session_data:
            return jsonify({"error": "Session not found"}), 404
        
        faiss_index_path = session_data.get('faiss_index_path')
        if not faiss_index_path:
            return jsonify({"error": "FAISS index file not found"}), 404
        
        #optional when deploy to cloud
        faiss_index_path = os.path.normpath(faiss_index_path)

        if not os.path.exists(faiss_index_path):
            return jsonify({"error": f"FAISS index file not found at {faiss_index_path}"}), 404

        bot = QueryBot(faiss_index_path=faiss_index_path, subscription_type=subscription_type)       
        bot.load_vector_store(embedding_model="models/text-embedding-004")
        response = await bot.answer_question(user_question, chat_model="gemini-1.5-pro")
        print("Bot Response:", response)
        
        # Check if a session already exists in chat_collection
        chat_session = chat_collection.find_one({"session_id": session_id})

        if not chat_session:
            new_session = {
                "username" : username,
                "session_id": session_id,
                "title": user_question[:50],
                "messages": [
                    {"role": "user", "content": user_question},
                    {"role": "bot", "content": response}
                ],
                "created_at": datetime.now(timezone.utc)
            }
            chat_collection.insert_one(new_session)
            return jsonify({"response": response, "username": username, "session_id": session_id, "title": new_session["title"]})
        else:
            chat_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {
                        "messages": {"$each": [
                            {"role": "user", "content": user_question},
                            {"role": "bot", "content": response}
                        ]}
                    }
                }
            )
            return jsonify({"response": response, "username": username, "session_id": session_id, "title": chat_session.get("title", "New Chat")})
    except Exception as e:
        print(f"Error in query_bot: {e}")
        return jsonify({"error": str(e)}), 500

######################## Get the Chats #####################

@app.route('/get-chat/<session_id>', methods=['GET'])
def get_chat(session_id):
    chat_data = chat_collection.find_one({"session_id": session_id})
    if chat_data:
        return jsonify({"messages": chat_data["messages"]})
    return jsonify({"error": "Chat not found"}), 404

####################### Stripe Payment ###############################

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        plan = data.get('plan')
        username = data.get('username')

        if plan != 'Plus':
            return jsonify({'error': 'Invalid plan selected'}), 400

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Subscription Plan - Plus',
                        },
                        'unit_amount': 2999,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:4242/webhook',
            cancel_url='http://127.0.0.1:4242/cancel',
            metadata={
                'plan': 'Plus',
                'username': username
            }
        )

        return jsonify({'sessionId': session.id, 'status': 'success'})

    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/webhook', methods=['POST'])
def webhook():
    endpoint_secret = os.getenv('WEBHOOK_ENDPOINT')
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print('Invalid payload', e)
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print('Invalid signature', e)
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'payment_intent.succeeded':
        session = event['data']['object']
        print(session)
        
        update_result = users_collection.update_one(
            {'username': session['metadata']['username']},
            {
                '$set': {
                    'plan': session['metadata']['plan'],
                    'Plan_Update_Date': datetime.now(timezone.utc)
                }
            }
        )

        if update_result.modified_count > 0:
            print(f"Successfully updated user {session['metadata']['username']}")
        else:
            print(f"User {session['metadata']['username']} not found or already updated")

    return jsonify({'status': 'success'})
    

####################### Fetch subscription status ####################

@app.route('/user_plan', methods=['GET'])
def get_user_credentials():
    username = session_manager.get_logged_in_user()
    if not username:
        return jsonify({"error": "User not logged in"}), 400 
    user = users_collection.find_one({"username": username})
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    subscription = user.get("plan")
    
    if not subscription:
        return jsonify({"error": "subscription not found"}), 404
    
    return jsonify({"username": username, "subscription": subscription})

######################## Delete Many Chats and account ##############################

@app.route('/delete_chats', methods=['DELETE'])
def delete_chats():
    username = session_manager.get_logged_in_user()
    if not username:
        return jsonify({"error": "User not logged in"}), 400

    vector_collection.delete_many({"username": username})
    chat_collection.delete_many({"username": username})
    return jsonify({"message": "Chats deleted successfully"})

@app.route('/delete-account', methods=['DELETE'])
def delete_account():
    username = session_manager.get_logged_in_user()
    if not username:
        return jsonify({"error": "User not logged in"}), 400

    users_collection.delete_one({"username": username})
    vector_collection.delete_many({"username": username})
    chat_collection.delete_many({"username": username})
    return jsonify({"message": "Account deleted successfully"})

######################## Success ############################

@app.route('/success')
def success():
    return render_template('success.html')

######################## Cancel ############################

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

######################## Logout #############################

@app.route('/logout')
def logout():
    session_manager.clear_user_session()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print('Backend is running!!!')
    app.run(host='0.0.0.0', port=5000, debug=True)