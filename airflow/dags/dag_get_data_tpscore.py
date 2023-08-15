import json
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from get_data_tpscore import get_endpoint_chain_data


# Default arguments for the DAG
default_args = {
    "owner": "active_developer",
    "retries": 5,
    "retry_delay": timedelta(minutes=1),
}

# Define the DAG
dag = DAG(
    dag_id="get_data_tpscore",
    default_args=default_args,
    start_date=datetime(2023, 7, 30, 9, 50),
    schedule_interval="*/10 * * * *",
    catchup=False,
)


# Read chain names from the JSON file
with open("/opt/airflow/dags/all_parachains_endpoints.json") as f:
    chains = json.load(f)


# Create tasks for each chain and add them to the DAG
for id, chain in enumerate(chains):
    task_id = f"get_data_{id}"
    task = PythonOperator(
        task_id=task_id,
        python_callable=get_endpoint_chain_data,
        op_kwargs={"chain_name": chain[0], "endpoint": chain[1]},
        dag=dag,
    )
