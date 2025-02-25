import csv
from collections import defaultdict
import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2) 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def read_csv(file_path):
    """Read diseases and symptoms from a CSV file."""
    disease_map = defaultdict(list)
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            disease = row['Disease']
            symptoms = row['Symptom'].split('^')
            disease_map[disease].extend(symptoms)
    
    # Remove duplicate symptoms for each disease
    for disease, symps in disease_map.items():
        disease_map[disease] = list(set(symps))
    
    return disease_map

def find_diseases_by_symptoms(symptoms, disease_map):
    """Find diseases based on a list of symptoms."""
    matched_diseases = defaultdict(list)
    pattern = set(symptoms)
    
    for disease, disease_symptoms in disease_map.items():
        if pattern.intersection(disease_symptoms):
            matched_diseases[disease].extend(disease_symptoms)
    
    return matched_diseases

def need_more_info():
    """Return a message indicating more information is needed."""
    return {'message': 'We need more information to determine the disease!'}

def calculate_sum_probability(sorted_poss, num):
    """Calculate the sum of probabilities for top N diseases."""
    count = 0
    total_sum = 0
    for i in range(len(sorted_poss)):
        if count < num:
            cur_poss = sorted_poss[i]
            total_sum += cur_poss[1]
            count += 1
    return total_sum

def calculate_probability_diff(diff_threshold, sorted_poss, num):
    """Check if the difference between probabilities exceeds a threshold."""
    total_sum = calculate_sum_probability(sorted_poss, num)
    avg = total_sum / num
    for i in range(num):
        cur = sorted_poss[i]
        if abs(cur[1] - avg) > diff_threshold:
            return False
    return True

def print_need_more_info():
    return "more information needed"

def calculate_possibility(diff_threshold, num, sum_threshold, user_symptoms, matched_diseases):
    """Calculate the overlap rate between user-provided symptoms and each possible disease's symptoms."""
    user_symptoms_set = set(user_symptoms)
    possibilities = {}
    
    for disease, disease_symptoms in matched_diseases.items():
        common_symptoms = user_symptoms_set.intersection(disease_symptoms)
        possibility = len(common_symptoms) / len(disease_symptoms)
        possibilities[disease] = possibility * 100
    
    # Sort possibilities by probability in descending order
    sorted_possibilities = sorted(possibilities.items(), key=lambda x: x[1], reverse=True)

    # Check if we need more information based on sum threshold and probability difference
    total_sum = calculate_sum_probability(sorted_possibilities, num)
    
    if total_sum < sum_threshold:
        return "more information needed"
    
    if calculate_probability_diff(diff_threshold, sorted_possibilities, num):
        return "more information needed"

    # Return top 10 diseases or fewer if less than 10 are available
    # return sorted_possibilities[:10]
    return sorted(possibilities.items(), key=lambda x:x[1], reverse = True)[:10]


# Path to your CSV file (update this path as needed)
file_path = '/home/xuejian/CS222/cleaned_database1.csv'
disease_map = read_csv(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    if 'symptoms' not in data:
        return jsonify({'error': 'No symptoms provided'}), 400
    
    user_symptoms = data['symptoms']
    
    # Default thresholds (you can adjust these values or pass them dynamically via request)
    diff_threshold = 10 # Example threshold for probability difference
    num_top_diseases = 3   # Number of top diseases to consider
    sum_threshold = 60  # Example threshold for sum of probabilities
    
    matched_diseases = find_diseases_by_symptoms(user_symptoms, disease_map)
    
    result_or_message = calculate_possibility(diff_threshold, num_top_diseases, sum_threshold, user_symptoms, matched_diseases)
    
    if isinstance(result_or_message, str):
        return jsonify({'message': result_or_message})
    
    # Otherwise, format and return the result as a list of diseases with their probabilities.
    result = [{'disease': item[0], 'possibility': item[1]} for item in result_or_message]
    
    return jsonify(result)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

genai.configure(api_key='AIzaSyAjA1-Yr0asaRzWv2Y4WrNiyIWdfdKY9CI')
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 2048,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction=(
    "Act as my personal medical assistant, dedicated to tracking and analyzing my health symptoms to identify "
    "potential conditions or illnesses. Whenever I describe symptoms or health concerns, follow these steps:\n\n"
    "Symptom Analysis: Carefully evaluate the symptoms I provide, cross-referencing them with common medical "
    "conditions. List potential issues or diagnoses with an explanation of how my symptoms align with each.\n\n"
    "Recommendations and Next Steps: Provide me with a suggested course of action, such as lifestyle adjustments, "
    "over-the-counter remedies, or advice on whether to consult a healthcare professional. Outline any further "
    "tests, diagnostics, or precautions that could help clarify or confirm potential issues.\n\n"
    "Ongoing Support: Follow up with questions or advice based on my symptoms and treatment progress. Keep track "
    "of changes over time, and offer continuous encouragement and reminders to maintain healthy habits or to take "
    "prescribed medications.\n\n"
    "Proactive Health Monitoring: Prompt me regularly about potential health screenings, wellness checks, or "
    "seasonal precautions I should consider. Aim to help me establish and maintain a proactive approach to my "
    "health and well-being.\n\n"
    "Throughout this process, be attentive, empathetic, and proactive in ensuring my physical and mental well-being."
  ),
)

chat_session = model.start_chat(history=[])


@app.route('/aichat')
@login_required
def aichat():
    disease = request.args.get('disease', '')
    return render_template('index2.html', disease=disease)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': '请输入用户名和密码。'}), 400

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=False)
            session.permanent = False
            return jsonify({'message': 'Login success!'}), 200
        else:
            return jsonify({'error': 'Wrong username or password'}), 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': '请输入用户名和密码。'}), 400

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return jsonify({'message': 'Successfully registered'}), 201

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Empty message.'}), 400

    try:
        response = chat_session.send_message(user_message)
        ai_response = response.text
        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

