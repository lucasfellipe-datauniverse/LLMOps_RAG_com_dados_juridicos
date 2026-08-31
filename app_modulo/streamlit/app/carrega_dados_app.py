#%%
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

#%%
def postgre_connection():
    # realiza conexao com o banco airflow
    conn = psycopg2.connect(dbname='airflow',
                            user='airflow',
                            password='airflow',
                            host='postgres',
                            port=5432)

    cur = conn.cursor(cursor_factory=RealDictCursor)

    return conn, cur

def gera_id(doc):
    # gera id atraves de conteudo do conteudo
    combined = f"{doc['text'][:10]}-{doc['question']}"

    hash_object = hashlib.md5(combined.encode())

    hash_hex = hash_object.hexdigest()

    docid = hash_hex[:8]

    return docid

def captura_user_e_avaliacao(doc_id, user_input, result, llm_score, response_time, hit_rate, mrr):
    # cria tabela e insere dados de avaliacao do modelo e do rag em relacao ao input
    conn, cur = postgre_connection()

    try:
        create = """
            CREATE TABLE IF NOT EXISTS user_avaliacao (
            id SERIAL NOT NULL PRIMARY KEY,
            doc_id VARCHAR(10) NOT NULL,
            user_input TEXT NOT NULL,
            result TEXT NOT NULL,
            llm_score DOUBLE PRECISION NOT NULL,
            response_time DOUBLE PRECISION NOT NULL,
            hit_rate DOUBLE PRECISION NOT NULL,
            mrr DOUBLE PRECISION NOT NULL,
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        cur.execute(create)
        conn.commit()
        print('tabela user_avaliacao criada com sucesso')

    except Exception as e:
        print(f'erro ao criar tabela user_avaliacao:{e}')
        conn.rollback()

    try: 
        insert = f"""
        INSERT INTO user_avaliacao (
        doc_id, user_input, result, llm_score, response_time, hit_rate, mrr
        ) 
        VALUES (
        '{doc_id}', '{user_input}', '{result}', '{llm_score}', '{response_time}', '{hit_rate}', '{mrr}'
        )
        """
        cur.execute(insert)
        conn.commit()
        print('dados inseridos com sucesso na tabela user_avaliacao')
    except Exception as e:
        print(f'erro ao inserir dados na tabela user_avaliacao:{e}')
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def captura_user_feedback(doc_id, user_input, result, response_time, issatisfield):
    # cria tabela e insere dados de feedback do usuario em relacao ao input
    conn, cur = postgre_connection()

    try:
        create = """
            CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY NOT NULL,
            doc_id VARCHAR(10) NOT NULL,
            user_input TEXT NOT NULL,
            result TEXT NOT NULL,
            response_time DOUBLE PRECISION NOT NULL,
            issatisfield BOOLEAN NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        cur.execute(create)
        conn.commit()

    except Exception as e:
        print(f'erro ao criar tabela user_feedback:{e}')
        conn.rollback()

    try:
        insert = f"""
        INSERT INTO user_feedback (
        doc_id, user_input, result, response_time, issatisfield        
        ) 
        VALUES (
        '{doc_id}', '{user_input}', '{result}', '{response_time}', '{issatisfield}'
        )"""        

        cur.execute(insert)
        conn.commit()
        print('dados inseridos na tabela user_feedback com sucesso')

    except Exception as e:
        print(f'erro ao inserir dados na tabela user_feedback:{e}')
        conn.rollback()

    finally:
        cur.close()
        conn.close()