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

# Example usage
if __name__ == "__main__":
    symptoms = ['headache', 'fever']  # User-provided symptoms list
    result = find_diseases_by_symptoms(symptoms)
    print(result)