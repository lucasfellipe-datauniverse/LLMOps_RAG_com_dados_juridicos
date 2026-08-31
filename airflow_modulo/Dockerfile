FROM apache/airflow:2.10.2

USER airflow

ENV AIRFLOW_HOME=/opt/airflow/airflow_modulo

WORKDIR /opt/airflow/airflow_modulo

COPY requirements.txt /opt/airflow/airflow_modulo/requirements.txt
COPY --chown=airflow:root dags /opt/airflow/airflow_modulo/dags

RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt