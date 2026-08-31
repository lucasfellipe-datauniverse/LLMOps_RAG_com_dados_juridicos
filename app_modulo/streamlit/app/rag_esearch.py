from elasticsearch import Elasticsearch

#%%
def get_esclient():
    # inicializa um cliente elasticsearch apontando pra URL com host do container do elasticsearch
    esclient = Elasticsearch('http://elasticsearch:9200')
                                     
    return esclient

def query_elsearch(esclient, query, indexname):
    # faz consulta usando query(input do usuario) nos dados indexados do elasticsearch
    search_body = {
        'size': 5,
        'query': {
            'bool':{
                'must':{
                    'multi_match':{
                        'query': query,
                        'fields':['question^2', 'text'],
                        'type': 'best_fields'
                    } 
                }
            }
        }
    }

    response = esclient.search(index=indexname, body=search_body)

    result_doc = []
    for hit in response['hits']['hits']:
        result_doc.append(hit['_source'])

    return result_doc    