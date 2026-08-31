#%%
from datetime import time
import streamlit as st
from app.rag_esearch import get_esclient, query_elsearch
from app.llm import llm_query
from app.evaluation import evaluate
from app.carrega_dados_app import gera_id, captura_user_e_avaliacao, captura_user_feedback

#%%
def main():
    st.set_page_config(page_title='LLM com RAG', page_icon=':100:', layout='wide')

    st.sidebar.title('LLM com RAG')
    st.sidebar.write('MLOps com IA genetativa com LLM e RAG')
    st.sidebar.markdown('---')

    st.title('IA generativa com RAG em dados Juridicos')
    st.write('Faça sua pergunta e receba respostas precisa sobre dados Juridicos')
    st.write('Faça sua pergunta em ingles pois os dados estao em ingles')

    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'docid' not in st.session_state:
        st.session_state.docid = None
    if 'userinput' not in st.session_state:
        st.session_state.userinput = None
    if 'userfeedback' not in st.session_state:
        st.session_state.userfeedback = None            
    if 'response_time' not in st.session_state:
        st.session_state.response_time = None

    userinput = st.text_input('Digite sua pergunta:')

    indexname = 'projetorag'

    try:
        esclient = get_esclient()

    except:
        print('O Elastic Search ainda nao carregou, atualize a pagina e tente novamente')    


    if st.button('Enviar'):
        if userinput:
            with st.spinner('Preparando resposta...'):
                try:
                    rag_outputs = query_elsearch(esclient, userinput, indexname)
                    context = '\n'.join(output['text'] for output in rag_outputs)

                    output, response_time = llm_query({'inputs': {'question': userinput.replace("'", ""), 'context': context}})

                    avaliacao = evaluate(lambda q: query_elsearch(esclient, q['question'], indexname))

                    result = output['answer'].replace("'", "")

                    docid = gera_id({'question': userinput, 'text': result})

                    captura_user_e_avaliacao(
                        docid,
                        userinput.replace("'", ""),
                        result,
                        output['score'],
                        response_time,
                        avaliacao['hit_rate'],
                        avaliacao['mrr']
                        )

                    st.session_state.result = result
                    st.session_state.docid = docid
                    st.session_state.userinput = userinput.replace("'", "")
                    st.session_state.response_time = response_time
                    st.session_state.userfeedback = False

                except Exception as e:
                    st.exception(e)
                    st.error("Erro ao processar a consulta. Verifique o ElasticSearch e tente novamente.")

        st.warning('Digite uma pergunta para continuar')                

    if st.session_state.result:
        st.subheader('Resposta:') 
        st.write(st.session_state.result)

        if not st.session_state.userfeedback:
            st.write('Voce esta satisfeito com a resposta?')
            column1, column2 = st.columns(2)
            with column1:
                if st.button('Satisfeito'):
                    captura_user_feedback(
                        st.session_state.docid,
                        st.session_state.userinput,
                        st.session_state.result,
                        st.session_state.response_time,
                        True
                    )
                    st.session_state.userfeedback = True
                    st.success('Feedback registrado: Satisfeito')

            with column2:
                if st.button('Não Satisfeito'):
                    captura_user_feedback(
                        st.session_state.docid,
                        st.session_state.userinput,
                        st.session_state.result,
                        st.session_state.response_time,
                        False
                    )
                    st.session_state.userfeedback = True
                    st.warning('Feedback registrado: Não satisfeito') 

if __name__ == '__main__':
    main()
