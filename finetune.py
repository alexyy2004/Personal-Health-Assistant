import google.generativeai as genai
import pandas as pd
import random
genai.configure(api_key='AIzaSyAjA1-Yr0asaRzWv2Y4WrNiyIWdfdKY9CI')
# for i, m in zip(range(5), genai.list_tuned_models()):
#   print(m.name)

df = pd.read_csv('cleaned_database1.csv', encoding='utf-8')

base_model = [
    m for m in genai.list_models()
    if "createTunedModel" in m.supported_generation_methods and
    "flash" in m.name][0]



df_selected = df.iloc[:, [1, -1]]
training_data = []


for index, row in df_selected.iterrows():
    training_data.append({
        'text_input': str(row.iloc[0]),  
        'output': str(row.iloc[1]),    
    })

name = f'medicore'
# operation = genai.create_tuned_model(
#     # You can use a tuned model here too. Set `source_model="tunedModels/..."`
#     source_model=base_model.name,
#     training_data=training_data,
#     id = name,
#     epoch_count = 100,
#     batch_size=4,
#     learning_rate=0.001,
# )

# print(operation.metadata)
# import time

# for status in operation.wait_bar():
#     time.sleep(30)
model = genai.GenerativeModel(f'tunedModels/{name}')

result = model.generate_content('I feel I have uncoordination')

print(result.text)
