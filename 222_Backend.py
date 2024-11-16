import csv
from collections import defaultdict

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
        # print(pattern)
        # print(disease_symptoms)
        # print(matched_diseases)
        # print("disease: ", disease, "\n")
        # print("symptom: ", disease_symptoms, "\n")
        if pattern.intersection(disease_symptoms):
            matched_diseases[disease].extend(disease_symptoms)
    
    return matched_diseases

def need_more_info():
    print("We need more information to determine the disease!!!\n")
    exit()

def calculate_sum_probability(sorted_poss, num):
    count = 0
    sum = 0
    for i in range(len(sorted_poss)):
        if count < num:
            cur_poss = sorted_poss[i]
            sum += cur_poss[1]
            count += 1
    return sum

def calculate_probability_diff(diff_threshold, sorted_poss, num):
    sum = calculate_sum_probability(sorted_poss, num)
    avg = sum / num
    for i in range(num):
        cur = sorted_poss[i]
        if abs(cur[1]-avg) > diff_threshold:
            return 0
    return 1

def calculate_possibility(diff_threshold, num, sum_threshold, user_symptoms, matched_diseases):
    """Calculate the overlap rate between user-provided symptoms and each possible disease's symptoms."""
    user_symptoms_set = set(user_symptoms)
    possibilities = {}
    
    for disease, disease_symptoms in matched_diseases.items():
        common_symptoms = user_symptoms_set.intersection(disease_symptoms)
        possibility = len(common_symptoms) / len(disease_symptoms)
        possibilities[disease] = possibility * 100
    
    # check whether need more info
    sorted_poss = sorted(possibilities.items(), key=lambda x:x[1], reverse = True)
    sum = calculate_sum_probability(sorted_poss, num)
    if sum < sum_threshold:
        need_more_info()
        
    difference = calculate_probability_diff(diff_threshold, sorted_poss, num)
    if difference == 1:
        need_more_info()

    # if not, return
    if len(possibilities.keys()) > 10:
        return sorted(possibilities.items(), key=lambda x:x[1], reverse = True)[:10]
    else:
        return sorted(possibilities.items(), key=lambda x:x[1], reverse = True)

# Example usage
if __name__ == "__main__":
    file_path = '/Users/yueyan/Documents/GitHub/Fall24-CS222/cleaned_database1.csv'  # Path to your CSV file
    symptoms = ['vertigo']  # User-provided symptoms list
    disease_map = read_csv(file_path)
    # print(disease_map)
    sum_threshold = 60
    diff_threshold = 10
    num = 3

    matched_diseases = find_diseases_by_symptoms(symptoms, disease_map)
    possibility = calculate_possibility(diff_threshold, num, sum_threshold, symptoms, matched_diseases)

    for i in possibility:
        disease_name = ""
        if "^" in i[0]:
            disease_name = i[0].replace("^", "/")
        else:
            disease_name = i[0]
        print("Possible Disease is:", disease_name, "\nwith possibility:", f"{i[1]:.3f}%")
        print("\n")
