FROM apache/airflow:2.5.3
USER root
RUN apt-get -y update
USER airflow
COPY airflow_requirements.txt /airflow_requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /airflow_requirements.txt