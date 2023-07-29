import json
import os
from datetime import datetime
import substrateinterface

import pymysql
import requests
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SUBSCAN_KEY = os.getenv("SUBSCAN_KEY")


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
    try:
        with connection.cursor() as cursor:
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


def get_current_utc_datetime():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def get_subscan_chain_data(chain_name, subscan_chain):
    print(f"Starting to get data for {chain_name}")
    headers = {"Content-Type": "application/json", "X-API-Key": SUBSCAN_KEY}

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

    (
        list_of_blocks,
        datetime_start,
        datetime_finish,
        block_start,
        block_finish,
    ) = get_last_100_blocks()

    time_delta_of_blocks = int((datetime_finish - datetime_start).total_seconds())

    total_n_transfers = 0

    for block in list_of_blocks:

        endpoint_block = f"https://{subscan_chain}.api.subscan.io/api/scan/block"
        raw_data_block = {"block_num": block}
        data_block_json = json.dumps(raw_data_block)

        request_block = requests.post(
            endpoint_block, headers=headers, data=data_block_json
        )

        balances_extrinsics = [
            extrinsic
            for extrinsic in request_block.json()["data"]["extrinsics"]
            if extrinsic["call_module"] == "balances"
        ]

        n_transfers = len(balances_extrinsics)
        total_n_transfers += n_transfers

    tps = total_n_transfers / time_delta_of_blocks
    avg_n_txns_in_block = total_n_transfers / 100

    print(
        block_start,
        block_finish,
        datetime_start,
        datetime_finish,
        avg_n_txns_in_block,
        tps,
    )
    print(f"Finished getting data for {chain_name}")
    upload_data(
    processing_started_at, 
    chain_name,
    datetime_start,
    datetime_finish,
    block_start,
    block_finish,
    avg_n_txns_in_block,
    tps)


def get_endpoint_chain_data(chain_name, endpoint):
    print(f"Starting to get data for {chain_name}")

    ws_provider = substrateinterface.SubstrateInterface(
        url=endpoint
    )   

    last_block = ws_provider.get_block()
    
    block_finish = last_block['header']['number']
    block_start = block_finish - 99 

    finish_block_timestamp_extrinsic = [extrinsic for extrinsic in last_block['extrinsics'] if extrinsic.value['call']['call_module']=="Timestamp"][0]
    datetime_finish = datetime.utcfromtimestamp(finish_block_timestamp_extrinsic.value['call']['call_args'][0]['value']/1000)

    first_block = ws_provider.get_block(block_number = block_start)

    start_block_timestamp_extrinsic = [extrinsic for extrinsic in first_block['extrinsics'] if extrinsic.value['call']['call_module']=="Timestamp"][0]
    datetime_start = datetime.utcfromtimestamp(start_block_timestamp_extrinsic.value['call']['call_args'][0]['value']/1000)

    time_delta_of_blocks = int((datetime_finish - datetime_start).total_seconds())

    total_n_transfers = 0 

    for block in range(block_start, block_finish+1):
        extrinsics = ws_provider.get_block(block_number=block)['extrinsics']
        balances_extrinsics = [extrinsic for extrinsic in extrinsics if extrinsic.value['call']['call_module']=="Balances"]
        n_transfers = len(balances_extrinsics)
        
        total_n_transfers += n_transfers

    tps = total_n_transfers / time_delta_of_blocks
    avg_n_txns_in_block = total_n_transfers / 100

    print(block_start, block_finish, datetime_start, datetime_finish, avg_n_txns_in_block, tps)

    print(f"Finished getting data for {chain_name}")

    upload_data(
    processing_started_at, 
    chain_name,
    datetime_start,
    datetime_finish,
    block_start,
    block_finish,
    avg_n_txns_in_block,
    tps)

def get_data():
    connect_to_db()
    global processing_started_at
    processing_started_at = get_current_utc_datetime()
    file_with_subscan_parachains = open("parachain_info/subscan_parachains.json")
    list_of_parachains_subscan = json.load(file_with_subscan_parachains)

    for parachain in list_of_parachains_subscan:
        get_subscan_chain_data(parachain[0], parachain[1])

    file_with_parachains_endpoints = open("parachain_info/endpoint_parachains.json")
    list_of_parachains_endpoints = json.load(file_with_parachains_endpoints)

    for parachain in list_of_parachains_endpoints:
        get_endpoint_chain_data(parachain[0], parachain[1])

    file_with_subscan_parachains.close()
    file_with_parachains_endpoints.close()
    connection.close()


if __name__ == "__main__":
    get_data()


