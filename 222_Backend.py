import mysql.connector
from collections import defaultdict

def connect_to_db():
    """ Create a connection to the MySQL database """
    connection = mysql.connector.connect(
        host='localhost',
        user='your_username',  # Replace with your username
        password='your_password',  # Replace with your password
        database='your_database'  # Replace with your database name
    )
    return connection

def find_diseases_by_symptoms(symptoms):
    """ Find diseases based on a list of symptoms """
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    
    # Build the query to match any of the given symptoms
    query = """
    SELECT disease_name, symptoms
    FROM diseases
    WHERE symptoms REGEXP %s
    """
    # Use a regular expression to match any of the given symptoms
    pattern = '|'.join([f"\\b{symptom}\\b" for symptom in symptoms])
    cursor.execute(query, (pattern,))
    
    # Store the results in a defaultdict
    disease_map = defaultdict(list)
    
    for row in cursor:
        disease = row['disease_name']
        disease_symptoms = row['symptoms'].split(',')
        disease_map[disease].extend(disease_symptoms)
    
    # Remove duplicate symptoms for each disease
    for disease, symps in disease_map.items():
        disease_map[disease] = list(set(symps))
    
    cursor.close()
    connection.close()
    
    return disease_map

def calculate_possibility(user_symptoms):
    """
    Calculate the overlap rate between user-provided symptoms and each possible disease's symptoms.
    
    Parameters:
    - user_symptoms (list): A list of symptoms provided by the user.
    - disease_map (dict): A dictionary where keys are disease names and values are lists of symptoms.
    
    Returns:
    - dict: A dictionary with disease names as keys and their overlap rate as values.
    """
    disease_map = find_diseases_by_symptoms(user_symptoms)
    user_symptoms_set = set(user_symptoms)
    possibilities = {}
    for disease in disease_map:
        disease_symptoms_set = set(symptoms)
        common_symptoms = user_symptoms_set.intersection(disease_symptoms_set)
        possibility = len(common_symptoms) / len(user_symptoms_set)
        possibilities[disease] = possibility
    
    return possibilities

# Example usage
if __name__ == "__main__":
    symptoms = ['headache', 'fever']  # User-provided symptoms list
    result = find_diseases_by_symptoms(symptoms)
    print(result)
    possibility = calculate_possibility(result)
    print(possibility)