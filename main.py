import os
import io
import asyncio
import uuid
import json
from datetime import datetime, timezone,timedelta
import stripe
import secrets
from flask import Flask, render_template,jsonify,request,redirect,url_for,flash,get_flashed_messages
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from Misc.conn import MongoDBConnector
from Misc.session import SessionManager
from ML_Models.pdf_extractor import PDFExtractor
from ML_Models.ML_Logic import QueryBot
from Subscriptions.pricing import PricingValidator

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
base_directory = os.environ.get("BASE_DIR")
stripe.api_key = os.environ.get("STRIPE_KEY")
stripe_pk = os.environ.get("STRIPE_PK")
CORS(app)

############################### EMAIL Configuration #################################

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("EMAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD") 
s = URLSafeTimedSerializer(app.secret_key)
mail = Mail(app)

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
    success_message = get_flashed_messages(category_filter=['success'])
    if session_manager.is_user_logged_in():
        return redirect(url_for('home'))
    return render_template('login.html',success_message=success_message)

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
    return render_template('home.html', stripe_pk=stripe_pk, username=username)

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
    
    if user['verification_status'] != 'yes':
        return jsonify({'error': 'Account not activated. Please check your email.'})
    
    current_date = datetime.utcnow()
    if user.get('plan') == 'Plus' and 'plan_expiry_date' in user and user['plan_expiry_date']:
        plan_expiry_date = user['plan_expiry_date']
        if current_date >= plan_expiry_date:
            users_collection.update_one(
                {'username': username},
                {'$set': {'plan': 'Free'},
                 '$unset': {'plan_update_date': "", 'plan_expiry_date': ""}}
            )
    
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
    
    existing_email = users_collection.find_one({'email': email})
    if existing_email:
        return jsonify({'error': 'This email is already registered with a different username'}), 400
    
    existing_useremail = users_collection.find_one({'username': username, 'email': email})
    if existing_useremail:
        return jsonify({'error': 'Username is already registered with this email'}), 400

    hashed_password = generate_password_hash(password)
    verification_token = secrets.token_hex(16)

    new_user = {
        'username': username,
        'password': hashed_password,
        'email': email,
        'verification_token': verification_token,
        'verification_status': 'no',
        "created_at": datetime.now(timezone.utc),
        'plan': 'Free'
    }
    users_collection.insert_one(new_user)

    send_verification_email(email, verification_token)

    return jsonify({'success': 'User registered successfully'})

def send_verification_email(email, token):
    verification_url = url_for('verify_email', token=token, _external=True)

    msg = Message(
        'account verification',
        sender=f"Hivaani <{app.config['MAIL_USERNAME']}>",
        recipients=[email]
    )
    msg.html = render_template('verification_email.html', verify_link=verification_url)
    mail.send(msg)

######################## Account Verification ################################

@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    user_data = users_collection.find_one({'verification_token': token})

    if not user_data:
        return jsonify({'error': 'Invalid or expired verification token'})

    users_collection.update_one(
        {'verification_token': token},
        {'$set': {'verification_status': 'yes'}, '$unset': {'verification_token': ""}}
    )

    flash('Your account has been activated successfully!', 'success')

    return redirect(url_for('index', verified='true'))

######################## Forgot Password link & Token ########################
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = users_collection.find_one({"email": email})
    username = user.get('username')
    if not user:
        return jsonify({"error": "User not found"}), 404

    token = s.dumps(email, salt='password-reset-salt')
    reset_link = url_for('reset_password', token=token, _external=True)

    try:
        msg = Message("Password Reset Request", 
                      sender=f"Hivaani <{app.config['MAIL_USERNAME']}>",
                      recipients=[email])
        msg.html = render_template('reset_pass_gmail.html', reset_link=reset_link, username=username)
        mail.send(msg)
        return jsonify({"message": "Password reset link sent to your email"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=3600)
            return render_template('reset_pass_link.html', token=token)
        except Exception as e:
            return "Invalid or expired token. Please request a new password reset.", 400
    
    if request.method == 'POST':
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=3600)
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 400

        data = request.form
        new_password = data.get('password')
        if not new_password:
            return jsonify({"error": "Password is required"}), 400

        hashed_password = generate_password_hash(new_password)
        result = users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
        
        if result.matched_count > 0:
            return jsonify({"message": "Password reset successfully! Redirecting you to the login page."}), 200
        else:
            return jsonify({"message": "Failed to update password. Please try again."}), 500

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

        if plan != 'Plus':
            return jsonify({'error': 'Invalid plan selected'}), 400

        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'ideal'],
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
            success_url='https://hivaani-zqhprsnjkq-ez.a.run.app/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://hivaani-zqhprsnjkq-ez.a.run.app/cancel?session_id={CHECKOUT_SESSION_ID}',
            )

        return jsonify({'sessionId': session.id, 'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
####################### Update plan and other details in DB After stripe payment success##############################

@app.route('/update-plan', methods=['POST'])
def update_plan():
    data = request.json
    plan = data.get('plan')
    username = session_manager.get_logged_in_user() 
    plan_update_date = datetime.fromisoformat(data.get('plan_update_date'))
    plan_expiry_date = datetime.fromisoformat(data.get('plan_expiry_date'))

    if not username:
        return jsonify({"error": "Username is required"}), 400

    result = users_collection.update_one(
        {"username": username},
        {"$set": {
            "plan": plan,
            "plan_update_date": plan_update_date,
            "plan_expiry_date": plan_expiry_date
        }}
    )

    if result.modified_count > 0:
        return jsonify({"message": "Plan updated successfully"}), 200
    else:
        return jsonify({"error": "User not found or no changes made"}), 404
    
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
    plan_update_date = user.get("plan_update_date")
    plan_expiry_date = user.get("plan_expiry_date")
    
    if not subscription:
        return jsonify({"error": "subscription not found"}), 404
    
    return jsonify({
        "username": username,
        "subscription": subscription,
        "plan_update_date": plan_update_date,
        "plan_expiry_date": plan_expiry_date
    })

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

######################## Edit Title of conversation row ################################

@app.route('/update_chat/<string:session_id>', methods=['PUT'])
def update_chat(session_id):
    username = session_manager.get_logged_in_user()
    if not username:
        return jsonify({"error": "User not logged in"}), 400

    data = request.get_json()
    new_title = data.get("title")

    if not new_title:
        return jsonify({"error": "New title is required"}), 400

    result = chat_collection.update_one(
        {"username": username, "session_id": session_id},
        {"$set": {"title": new_title}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Chat not found"}), 404

    return jsonify({"message": "Title updated successfully"})


######################## Delete Converssation row ######################################

@app.route('/delete_chat/<string:session_id>', methods=['DELETE'])
def delete_chat(session_id):
    username = session_manager.get_logged_in_user()
    if not username:
        return jsonify({"error": "User not logged in"}), 400

    result_by_session = chat_collection.delete_one({"username": username, "session_id": session_id})
    if result_by_session.deleted_count > 0:
        return jsonify({"message": "Chat deleted successfully"})

    return jsonify({"error": "Chat not found"}), 404


######################## Contact Email #################################################

@app.route('/send-email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        if not name or not email or not message:
            return jsonify({"status": "error", "message": "Please fill out all required fields."}), 400

        try:
            msg = Message(
                subject=f"New Contact Form Submission from {name}",
                sender=email,
                recipients=['htechno0786@gmail.com'] 
            )
            msg.html = render_template(
                'contact_email.html',
                name=name,
                email=email,
                phone=phone,
                message=message
            )
            mail.send(msg)
            return jsonify({"status": "success", "message": "Your message has been sent successfully!"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to send the message. Error: {str(e)}"}), 500

    return render_template('contact.html')

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
    app.run(host="0.0.0.0", port=8080, debug=True)