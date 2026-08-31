from pathlib import Path

#%%
import pandas as pd

#%%
def hit_rate(relevance_total):
    # calcula o hit rate
    cnt = 0
    for line in relevance_total:
        if True in line:
            cnt += 1
 
    return cnt / len(relevance_total)            

def mrr(relevance_total):
    # calcula o mean reciprocal rank
    score = 0

    for line in relevance_total:
        for rank in line:
            if line[rank] == True:
                score += 1 / (rank + 1) 
            break

    return score / len(relevance_total)

def evaluate(research_funtion):
    # verifica se o rag buscou informacao correta ou incorreta para a requisicao
                                
    dataset_path = Path(__file__).parent / 'dados_historicos' / 'dataset.csv'
    ground_truth = pd.read_csv(dataset_path).to_dict(orient='records')

    relevance_total = []

    for line in ground_truth:
        doc_id = line['document']

        results = research_funtion(line) # research_fuc fara..

        relevance = [doc_id==line_results['doc_id'] for line_results in results]

        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total)
    }    
 