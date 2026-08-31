#%%
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from datetime import timedelta
from modulo_dados.carrega_dados import cria_tabela, insere_dados_json, insere_dados_csv, cria_indece

#%%
# puipeline de engenharia de dados para carga extracao e indexacao de dados para RAG

default_args = {
    'owner': 'Lucas',
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(hours=1)
}

dag = DAG(
    'engenharia_de_dados_para_RAG',
    default_args=default_args,
    schedule='0 0 * * *',
    description='Pipeline de carga, extracao e indexacao de dados para rag'
)

task_cria_tabela = PythonOperator(
    task_id='cria_tabela', # cria tabela dados_juridicos no banco de dados do airflow
    python_callable=cria_tabela,
    dag=dag
)

task_insere_dados_json = PythonOperator(
    task_id='insere_dados_json', # insere dados json na tabela dados_juridicos
    python_callable=insere_dados_json,
    dag=dag
)

task_insere_dados_csv = PythonOperator(
    task_id='insere_dados_csv', # insere dados csv na tabela dados_juridicos
    python_callable=insere_dados_csv,
    dag=dag
)

task_indexa_dados = PythonOperator(
    task_id='indexa_dados',
    python_callable=cria_indece,
    dag=dag
)

task_cria_tabela >> task_insere_dados_json >> task_insere_dados_csv >> task_indexa_dados
