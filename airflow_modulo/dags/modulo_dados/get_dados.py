#%%
from modulo_dados.connection import postgre_connection

#%%
def extrai_dados():
    # extrai os dados necessarios para RAG
    conn, cur = postgre_connection()        
    query = 'select doc_id, question, answer from dados_juridicos'
    alldata = []

    cur.execute(query)
    dados = cur.fetchall()
    
    for dado in dados:
        alldata.append(dado)

    cur.close()
    conn.close()

    return alldata         