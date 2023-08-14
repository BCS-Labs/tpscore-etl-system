USE tpscore_data;

CREATE TABLE chain_info(
	chain_name varchar(100) PRIMARY KEY,
    blocktime float
);

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

INSERT INTO chain_info VALUES("Acala", 12);
INSERT INTO chain_info VALUES("Ajuna Network", 12);
INSERT INTO chain_info VALUES("Aleph Zero", 1);
INSERT INTO chain_info VALUES("Assethub Polkadot", 12);
INSERT INTO chain_info VALUES("Astar", 12);
INSERT INTO chain_info VALUES("Aventus Network", 12);
INSERT INTO chain_info VALUES("Bitfrost", 12);
INSERT INTO chain_info VALUES("Bitgreen", 12);
INSERT INTO chain_info VALUES("Centrifuge", 12);
INSERT INTO chain_info VALUES("Clover", 6);
INSERT INTO chain_info VALUES("Collectives", 12);
INSERT INTO chain_info VALUES("Composable Finance", 12);
INSERT INTO chain_info VALUES("Crust", 12);
INSERT INTO chain_info VALUES("Darwinia", 12);
INSERT INTO chain_info VALUES("Efinity", 6);
INSERT INTO chain_info VALUES("Equilibrium", 12);
INSERT INTO chain_info VALUES("Frequency", 12);
INSERT INTO chain_info VALUES("Hashed Network", 12);
INSERT INTO chain_info VALUES("HydraDX", 12);
INSERT INTO chain_info VALUES("Integritee", 12);
INSERT INTO chain_info VALUES("Interlay", 12);
INSERT INTO chain_info VALUES("Kapex", 12);
INSERT INTO chain_info VALUES("KILT", 12);
INSERT INTO chain_info VALUES("Kylin Network", 12);
INSERT INTO chain_info VALUES("Litentry", 12);
INSERT INTO chain_info VALUES("Manta Network", 12);
INSERT INTO chain_info VALUES("Moonbeam", 12);
INSERT INTO chain_info VALUES("Nodle", 12);
INSERT INTO chain_info VALUES("OAK Network", 12);
INSERT INTO chain_info VALUES("OriginTrail", 12);
INSERT INTO chain_info VALUES("Parallel Finance", 12);
INSERT INTO chain_info VALUES("Pendalum", 12);
INSERT INTO chain_info VALUES("Phala", 12);
INSERT INTO chain_info VALUES("Polkadex", 12);
INSERT INTO chain_info VALUES("Polkadot", 6);
INSERT INTO chain_info VALUES("Subsocial", 12);
INSERT INTO chain_info VALUES("t3rn", 12);
INSERT INTO chain_info VALUES("Unique", 12);
INSERT INTO chain_info VALUES("Zeitgeist", 12);