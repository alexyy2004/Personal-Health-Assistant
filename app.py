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

def calculate_possibility(user_symptoms, matched_diseases):
    """Calculate the overlap rate between user-provided symptoms and each possible disease's symptoms."""
    user_symptoms_set = set(user_symptoms)
    possibilities = {}
    
    for disease, disease_symptoms in matched_diseases.items():
        common_symptoms = user_symptoms_set.intersection(disease_symptoms)
        possibility = len(common_symptoms) / len(disease_symptoms)
        possibilities[disease] = possibility * 100
    
    if len(possibilities.keys()) > 10:
        return sorted(possibilities.items(), key=lambda x:x[1], reverse=True)[:10]
    else:
        return sorted(possibilities.items(), key=lambda x:x[1], reverse=True)


file_path = 'E:\CS222_Project\cleaned_database1.csv'  
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
    
    matched_diseases = find_diseases_by_symptoms(user_symptoms, disease_map)
    possibility = calculate_possibility(user_symptoms, matched_diseases)
    
    result = [{'disease': item[0], 'possibility': item[1]} for item in possibility]
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
