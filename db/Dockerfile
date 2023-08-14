FROM mysql/mysql-server:latest

ENV MYSQL_USER=user_tpscore \
    MYSQL_PASSWORD=pass_tpscore \
    MYSQL_DATABASE=tpscore_data \
    MYSQL_ROOT_PASSWORD=root 
    
COPY db_schema.sql /docker-entrypoint-initdb.d
EXPOSE 3306/tcp