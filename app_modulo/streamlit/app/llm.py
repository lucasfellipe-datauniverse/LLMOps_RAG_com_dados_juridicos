#%%
import os
import datetime
import requests
#%%
def llm_query(payload):
    # faz consulta no llm usando a pergunda e o contexto(obtido dos dados do elastichsearch)
    API_URI = 'https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad'

    # HAGGINGFACE_KEY variavel do compose que armazena a key do modelo
    headers = {'Authorization': f'Bearer {os.getenv('HAGGINGFACE_KEY')}'}

    starttime = datetime.time()
    response = requests.post(API_URI, headers=headers, json=payload)
    endtime = datetime.time()

    response_time = round(endtime - starttime, 2)

    return response.json, response_time 
