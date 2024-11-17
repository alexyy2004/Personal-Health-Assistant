from flask import Flask, render_template, request, jsonify
import csv
from collections import defaultdict

app = Flask(__name__)

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
    
    if not calculate_probability_diff(diff_threshold, sorted_possibilities, num):
        return "more information needed"

    # Return top 10 diseases or fewer if less than 10 are available
    return sorted_possibilities[:10]

# Path to your CSV file (update this path as needed)
file_path = 'E:/CS222_Project/cleaned_database1.csv'
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
    diff_threshold = 60 # Example threshold for probability difference
    num_top_diseases = 10   # Number of top diseases to consider
    sum_threshold = 3  # Example threshold for sum of probabilities
    
    matched_diseases = find_diseases_by_symptoms(user_symptoms, disease_map)
    
    result_or_message = calculate_possibility(diff_threshold, num_top_diseases, sum_threshold, user_symptoms, matched_diseases)
    
    if isinstance(result_or_message, str):
        return jsonify({'message': result_or_message})
    
    # Otherwise, format and return the result as a list of diseases with their probabilities.
    result = [{'disease': item[0], 'possibility': item[1]} for item in result_or_message]
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)