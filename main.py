from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from langchain_community.utilities.sql_database import SQLDatabase
import torch
import sys
import time
from threading import Thread
import shutil
#import re

from huggingface_hub import login
login(token="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")
device = 'cuda'
sys.stdout.reconfigure(encoding='utf-8')
tokenizer = AutoTokenizer.from_pretrained("epfl-llm/meditron-7b")
model = AutoModelForCausalLM.from_pretrained("epfl-llm/meditron-7b", torch_dtype=torch.float16, device_map=device)



def talk_with_model(model, message):
    
    text = tokenizer.apply_chat_template(
        message,
        tokenize=False,
        add_generation_prompt=True
    )
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    model_input = tokenizer([text], return_tensors='pt', truncation = True).to(device)
    attention_mask = torch.ones(model_input.input_ids.shape, dtype=torch.long, device=device)
    generated_ids = model.generate(
        model_input.input_ids,
        max_new_tokens=1024,
        streamer=streamer,
        attention_mask=attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        num_return_sequences=1,
        top_k = 50,
        top_p = 0.95,
        num_beams = 1,
        temperature=0.6,
    )
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_input.input_ids, generated_ids)]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response
       
        
if  __name__ == '__main__':
    while True:

        print(f'How can I help you? \n')
        message = input()  
        if message == "Goodbye":
            break
        Messages = [
            {'role': 'system', 'content': f"""You are my personal medical assistant. Please answer all of my medical questions with accurate, up-to-date, and clear information. Provide detailed explanations in an easy-to-understand manner, and support your answers with relevant examples when appropriate. Remember to be professional, empathetic, and respectful in all your responses."""},
                
            {'role': 'user', 'content': f""" {message}"""},
        ]
        
        response = talk_with_model(model, Messages)
        
        

        print(f'{response} \n')
        
        
