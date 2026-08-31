#%%
import os 
import orjsonl
import hashlib
import pandas as pd
# from shutil import ExecError
from elasticsearch import Elasticsearch
from modulo_dados.connection import postgre_connection
from modulo_dados.get_dados import extrai_dados

#%% 

def gera_id(doc):
    # gera id atraves de conteudo do conteudo
    combined = f"{doc['text'][:10]}-{doc['question']}"

    hash_object = hashlib.md5(combined.encode())

    hash_hex = hash_object.hexdigest()

    docid = hash_hex[:8]

    return docid

def cria_tabela():
    # cria tabela dados_juridicos no banco do airflow
    conn, cur = postgre_connection()

    try:
        criacao = """CREATE TABLE dados_juridicos (
                     id serial PRIMARY KEY,
                     doc_id VARCHAR(10),
                     question TEXT NOT NULL,
                     answer TEXT NOT NULL);"""

        cur.execute(criacao)
        conn.commit()
 
    except Exception as e:
        print(e)

        try:
            trunc = """TRUNCATE TABLE dados_juridicos;"""
            cur.execute(trunc)

        except Exception as e:
            print(e)    

    finally:
        cur.close()
        conn.close()                    


def insere_dados_json():
    # insere dados json na tabela dados_juridicos do banco do airflow    
    alldata = []

    dados_json = orjsonl.load(f'{os.getcwd()}/dags/dados/dataset1.jsonl')

    conn, cur = postgre_connection()

    for data in dados_json[0:25]:

        data = {'question': str(data['question']),
                'text': str(data['answer'])}

        docid = gera_id(data)

        alldata.append((str(docid), str(data['question']), data['text']))

    try:
        args = ','.join(
                        cur.mogrify('(%s, %s, %s)', item).decode('utf-8')
                        for item in alldata)

        inserir = 'INSERT INTO dados_juridicos (doc_id, question, answer) VALUES' + (args)

        cur.execute(inserir)
        conn.commit()

        print('dados inseridos na tabela dados_juridicos')

    except Exception as e:
        print(f'erro ao inserir dados:{e}')
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

def insere_dados_csv():
    # insere dados csv na tabela dados_juridicos do banco do airflow    
    alldata = []

    dados_csv = (
        pd.read_csv(f'{os.getcwd()}/dags/dados/dataset2.csv')
        .dropna(subset=['case_title', 'case_text'])
        .head(25)
    )

    conn, cur = postgre_connection()

    for _, data in dados_csv.head(25).iterrows():

        data = {'question': str(data['case_title']),
                'text': str(data['case_text'])}

        docid = gera_id(data)

        alldata.append((str(docid), str(data['question']), str(data['text'])))

    try:
        args = ','.join(
                        cur.mogrify('(%s, %s, %s)', item).decode('utf-8')
                        for item in alldata)
        
        inserir = 'INSERT INTO dados_juridicos (doc_id, question, answer) VALUES' + (args)

        cur.execute(inserir)
        conn.commit()
        print('dados inseridos com sucesso')

    except Exception as e:
        print(f'erro ao inserir dados: {e}')
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()                


def cria_indece():
    # cria index e indexa dados no elastic search
    esCliente = Elasticsearch('http://elasticsearch:9200')

    indexName = 'projetorag'

    indexSettings = {
            'settings':{
                'number_of_shards': 1,
                'number_of_replicas': 0
             },
             'mappings':{
                 'properties':{
                     'question': {'type': 'text'},
                     'text': {'type': 'text'}
                  }
            }
    }

    if esCliente.indices.exists(index=indexName):
        esCliente.indices.delete(index=indexName)

    esCliente.indices.create(index=indexName, body=indexSettings)

    data = extrai_dados()
    
    for doc in data:
        doc = {'doc_id': doc['doc_id'],
                'question': doc['question'],
                'text': doc['answer']}
        try:
            esCliente.index(index=indexName, document=doc)            
        except Exception as e:
            print(f'erro ao indexar dados:{e}')
    print('dados indexados com sucesso')
