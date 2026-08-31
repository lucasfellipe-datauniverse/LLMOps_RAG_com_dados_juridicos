#%%
import os
import time
import requests
#%%
def llm_query(payload):
    # faz consulta no llm usando a pergunda e o contexto(obtido dos dados do elastichsearch)
    API_URI = 'https://router.huggingface.co/hf-inference/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad'

    headers = {'Authorization': f"Bearer {os.getenv('HUGGINGFACE_KEY')}"}

    starttime = time.time()
    response = requests.post(API_URI, headers=headers, json=payload, timeout=60)
    endtime = time.time()
 
    response_time = round(endtime - starttime, 2)
    
    return response.json(), response_time  