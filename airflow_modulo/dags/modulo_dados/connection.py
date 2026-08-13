#%%
import psycopg2
from psycopg2.extras import RealDictCursor

#%%
def postgre_connection():
    # realiza conexao com o banco airflow
    conn = psycopg2.connect(dbname='airflow',
                            user='airflow',
                            password='airflow',
                            host='postgre',
                            port=5432)

    cur = conn.cursor(cursor_factory=RealDictCursor)

    return conn, cur
