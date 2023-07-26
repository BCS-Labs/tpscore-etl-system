CREATE DATABASE tpscore_data;

USE tpscore_data;

CREATE TABLE tps(
	processing_started_at datetime,
	chain_name varchar(100),
    datetime_start datetime,
    datetime_finish datetime,
    block_start int,
    block_finish int,
    avg_n_txns_in_block float,
    tps float,
    PRIMARY KEY (processing_started_at, chain_name),
    FOREIGN KEY (chain_name) REFERENCES chain_info(chain_name)
);

CREATE TABLE chain_info(
	chain_name varchar(100) PRIMARY KEY,
    blocktime float
);

