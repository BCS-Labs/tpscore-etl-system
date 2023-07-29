import json
import os
from datetime import datetime
import substrateinterface

import pymysql
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SUBSCAN_KEY = os.getenv("SUBSCAN_KEY")

# List of parachain endpoints
endpoint_parachains = [ 
    ["Ajuna Network", "wss://rpc-parachain.ajuna.network"],
    ["Aventus Network", "wss://public-rpc.mainnet.aventus.io"],
    ["Bitgreen", "wss://mainnet.bitgreen.org"],
    ["Collectives", "https://collectives.api.onfinality.io/rpc?apikey=28fd449f-ad7c-4ffb-baf5-391e1d16b92c"],
    ["Frequency", "wss://frequency-rpc.dwellir.com"],
    ["Hashed Network", "wss://c1.hashed.live"],
    ["Kapex", "wss://k-ui.kapex.network"],
    ["Kylin Network", "wss://polkadot.kylin-node.co.uk"],
    ["Litentry", "wss://rpc.litentry-parachain.litentry.io"],
    ["Manta Network", "wss://ws.manta.systems"],
    ["OAK Network", "https://turing-rpc.dwellir.com"],
    ["Pendalum", "wss://rpc-pendulum.prd.pendulumchain.tech:443"],
    ["Subsocial", "wss://para.f3joule.space"],
    ["t3rn", "wss://ws.t3rn.io"]
]

# List of subscan api endpoints
subscan_parachains = [
    ["Polkadot","polkadot"],
    ["Darwinia", "darwinia"],
    ["Acala", "acala"],
    ["Aleph Zero", "alephzero"],
    ["Astar", "astar"],
    ["Bitfrost", "bifrost"],
    ["Centrifuge", "centrifuge"],
    ["Clover", "clv"],
    ["Composable Finance", "composable"],
    ["Crust", "crust"],
    ["Efinity", "efinity"],
    ["Equilibrium", "equilibrium"],
    ["HydraDX", "hydradx"],
    ["Integritee", "integritee"],
    ["Interlay", "interlay"],
    ["KILT", "spiritnet"],
    ["Moonbeam", "moonbeam"],
    ["Nodle","nodle"],
    ["OriginTrail", "origintrail"],
    ["Parallel Finance","parallel"],
    ["Phala", "phala"],
    ["Polkadex", "polkadex"],
    ["Assethub Polkadot", "assethub-polkadot"],
    ["Unique", "unique"],
    ["Zeitgeist", "zeitgeist"]
]


# Function to connect to the database
def connect_to_db():
    global connection
    connection = pymysql.connect(
        host=HOST,
        user=USERNAME,
        password=PASSWORD,
        db="tpscore_data",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

# Function to upload data to the database
def upload_data(
    processing_started_at,
    chain_name,
    datetime_start,
    datetime_finish,
    block_start,
    block_finish,
    avg_n_txns_in_block,
    tps
):
    """
    Uploads TPS data to the database.

    Parameters:
        processing_started_at (datetime): The UTC datetime when data processing started.
        chain_name (str): Name of the parachain.
        datetime_start (datetime): The UTC datetime of the first block processed.
        datetime_finish (datetime): The UTC datetime of the last block processed.
        block_start (int): Block number of the first block processed.
        block_finish (int): Block number of the last block processed.
        avg_n_txns_in_block (float): Average number of transactions in each block.
        tps (float): Transactions Per Second (TPS) for the processed data.

    Returns:
        None
    """
    try:
        with connection.cursor() as cursor:
            # SQL query to insert data into the database table 'tps'
            sql = "INSERT INTO tps(processing_started_at, chain_name, datetime_start, datetime_finish, block_start, block_finish, avg_n_txns_in_block, tps) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    processing_started_at,
                    chain_name,
                    datetime_start,
                    datetime_finish,
                    block_start,
                    block_finish,
                    avg_n_txns_in_block,
                    tps
                ),
            )

        connection.commit()
        print(f"Records uploaded successfully at {processing_started_at}")
    except Exception as e:
        print(f"There was the issue: {e}")


# Function to get the current UTC datetime
def get_current_utc_datetime():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


# Function to get data from Subscan API for a specific parachain
def get_subscan_chain_data(chain_name, subscan_chain):
    """
    Fetches TPS data from Subscan API for a specific parachain.

    Parameters:
        chain_name (str): Name of the parachain or chain.
        subscan_chain (str): Subscan chain name associated with the parachain.

    Returns:
        None
    """
    print(f"Starting to get data for {chain_name}")
    headers = {"Content-Type": "application/json", "X-API-Key": SUBSCAN_KEY}

    # Helper function to get data for the last 100 blocks from Subscan API
    def get_last_100_blocks():
        endpoint_blocks = f"https://{subscan_chain}.api.subscan.io/api/scan/blocks"
        raw_data_blocks = '{"row": 100,"page": 0}'
        request_blocks = requests.post(
            endpoint_blocks, headers=headers, data=raw_data_blocks
        )

        blocks_data = request_blocks.json()

        datetime_start = datetime.utcfromtimestamp(
            blocks_data["data"]["blocks"][-1]["block_timestamp"]
        )

        datetime_finish = datetime.utcfromtimestamp(
            blocks_data["data"]["blocks"][0]["block_timestamp"]
        )

        block_start = blocks_data["data"]["blocks"][-1]["block_num"]
        block_finish = blocks_data["data"]["blocks"][0]["block_num"]

        list_of_blocks = [block["block_num"] for block in blocks_data["data"]["blocks"]]

        return (
            list_of_blocks,
            datetime_start,
            datetime_finish,
            block_start,
            block_finish,
        )

    # Get the data for the last 100 blocks
    (
        list_of_blocks,
        datetime_start,
        datetime_finish,
        block_start,
        block_finish,
    ) = get_last_100_blocks()

     # Calculate the time difference in seconds between the first and last block
    time_delta_of_blocks = int((datetime_finish - datetime_start).total_seconds())

    # Initialize total number of transfers
    total_n_transfers = 0

    # Loop through each block to count the number of balance transfers (extrinsics)
    for block in list_of_blocks:

        # Get block data for a specific block number from Subscan API
        endpoint_block = f"https://{subscan_chain}.api.subscan.io/api/scan/block"
        raw_data_block = {"block_num": block}
        data_block_json = json.dumps(raw_data_block)

        request_block = requests.post(
            endpoint_block, headers=headers, data=data_block_json
        )

        # Extract extrinsics related to balances 
        balances_extrinsics = [
            extrinsic
            for extrinsic in request_block.json()["data"]["extrinsics"]
            if extrinsic["call_module"] == "balances"
        ]

        # Count the number of transfers in the block
        n_transfers = len(balances_extrinsics)
        total_n_transfers += n_transfers

    # Calculate the TPS and average number of transactions in each block
    tps = total_n_transfers / time_delta_of_blocks
    avg_n_txns_in_block = total_n_transfers / 100

    # Print the results for the parachain
    print(
        block_start,
        block_finish,
        datetime_start,
        datetime_finish,
        avg_n_txns_in_block,
        tps,
    )

    print(f"Finished getting data for {chain_name}")

    # Upload the data to the database
    upload_data(
    processing_started_at, 
    chain_name,
    datetime_start,
    datetime_finish,
    block_start,
    block_finish,
    avg_n_txns_in_block,
    tps)

# Function to get data from an endpoint for a specific parachain
def get_endpoint_chain_data(chain_name, endpoint):
    """
    Fetches TPS data from an endpoint for a specific parachain.

    Parameters:
        chain_name (str): Name of the parachain or chain.
        endpoint (str): URL of the endpoint to interact with the parachain.

    Returns:
        None
    """
    print(f"Starting to get data for {chain_name}")

    # Create a SubstrateInterface object to interact with the parachain node
    ws_provider = substrateinterface.SubstrateInterface(
        url=endpoint
    )   

    # Get the latest block data
    last_block = ws_provider.get_block()
    
    # Calculate the block number of the first block (100 blocks range)
    block_finish = last_block['header']['number']
    block_start = block_finish - 99 

    # Extract the timestamps for the first and last blocks
    finish_block_timestamp_extrinsic = [extrinsic for extrinsic in last_block['extrinsics'] if extrinsic.value['call']['call_module']=="Timestamp"][0]
    datetime_finish = datetime.utcfromtimestamp(finish_block_timestamp_extrinsic.value['call']['call_args'][0]['value']/1000)

    first_block = ws_provider.get_block(block_number = block_start)
    start_block_timestamp_extrinsic = [extrinsic for extrinsic in first_block['extrinsics'] if extrinsic.value['call']['call_module']=="Timestamp"][0]
    datetime_start = datetime.utcfromtimestamp(start_block_timestamp_extrinsic.value['call']['call_args'][0]['value']/1000)

    # Calculate the time difference in seconds between the first and last block
    time_delta_of_blocks = int((datetime_finish - datetime_start).total_seconds())

    # Initialize total number of transfers
    total_n_transfers = 0 

    # Loop through each block to count the number of balance transfers (extrinsics)
    for block in range(block_start, block_finish+1):
        extrinsics = ws_provider.get_block(block_number=block)['extrinsics']
        balances_extrinsics = [extrinsic for extrinsic in extrinsics if extrinsic.value['call']['call_module']=="Balances"]
        n_transfers = len(balances_extrinsics)
        
        total_n_transfers += n_transfers

    # Calculate the TPS and average number of transactions in each block
    tps = total_n_transfers / time_delta_of_blocks
    avg_n_txns_in_block = total_n_transfers / 100

    # Print the results for the parachain
    print(block_start, block_finish, datetime_start, datetime_finish, avg_n_txns_in_block, tps)
    print(f"Finished getting data for {chain_name}")

    # Upload the data to the database
    upload_data(
    processing_started_at, 
    chain_name,
    datetime_start,
    datetime_finish,
    block_start,
    block_finish,
    avg_n_txns_in_block,
    tps)


# Function to fetch data for all parachains
def get_data():
    connect_to_db()
    global processing_started_at
    processing_started_at = get_current_utc_datetime()

    # Loop through each parachain and fetch data from Subscan API
    for parachain in subscan_parachains:
        get_subscan_chain_data(parachain[0], parachain[1])

    # Loop through each parachain and fetch data from an endpoint
    for parachain in endpoint_parachains:
        get_endpoint_chain_data(parachain[0], parachain[1])

    connection.close()


if __name__ == "__main__":
    get_data()


