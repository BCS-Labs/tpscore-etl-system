1. clone the project 

Create db container:
1. cd db
2. docker build -t mysql_tpscore .
3. docker run -p 3305:3306/tcp --name db_mysql -d mysql_tpscore

Create airflow container:
1. cd ..
2. cd airflow
3. docker compose up airflow-init
4. docker build .
5. docker compose up -d

Create a network and connect containers:
1. docker network create net_tpscore
2. docker network connect net_tpscore db_mysql
3. docker network connect net_tpscore <airflow_scheduler_container_id>

Note, you can find <airflow_scheduler_container_id> by running docker ps command.

Go to Airflow UI:
1. Go to http://localhost:8080/ 
2. Login with (airflow, airflow)
3. Click run get_data_tpscore DAG
