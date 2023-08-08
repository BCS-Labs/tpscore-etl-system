from datetime import datetime
from unittest.mock import patch

from pymysql import cursors

import get_data_tpscore

# Example connection parameters for testing
TEST_HOST = "localhost"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"


def test_connect_to_db():
    with patch("get_data_tpscore.connect") as mock_connect:
        # Arrange
        expected_connection_params = {
            "host": TEST_HOST,
            "user": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "db": "tpscore_data",
            "charset": "utf8mb4",
            "cursorclass": cursors.DictCursor,
        }

        # Act
        get_data_tpscore.connect_to_db(
            expected_connection_params["host"],
            expected_connection_params["user"],
            expected_connection_params["password"],
        )

        # Assert
        mock_connect.assert_called_once_with(**expected_connection_params)


def test_upload_data():
    with patch("get_data_tpscore.connect_to_db") as mock_connect_to_db:
        mock_connection = mock_connect_to_db.return_value
        cursor = mock_connection.cursor
        enter_context_manager = cursor.return_value.__enter__.return_value

        # Arrange
        processing_started_at = "2023-08-03 12:40:56"
        chain_name = "Test Chain"
        datetime_start = "2023-08-03 12:34:00"
        datetime_finish = "2023-08-03 12:40:00"
        block_start = 1001
        block_finish = 1100
        avg_n_txns_in_block = 10.5
        tps = 5.7

        # Act
        get_data_tpscore.upload_data(
            processing_started_at,
            chain_name,
            datetime_start,
            datetime_finish,
            block_start,
            block_finish,
            avg_n_txns_in_block,
            tps,
        )

        # Assert
        expected_sql_query = "INSERT INTO tps(processing_started_at, chain_name, datetime_start, datetime_finish, block_start, block_finish, avg_n_txns_in_block, tps) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        expected_params = (
            processing_started_at,
            chain_name,
            datetime_start,
            datetime_finish,
            block_start,
            block_finish,
            avg_n_txns_in_block,
            tps,
        )

        mock_connect_to_db.assert_called_once()
        cursor.assert_called_once()
        enter_context_manager.execute.assert_called_once_with(
            expected_sql_query, expected_params
        )
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()


def test_get_endpoint_chain_data():
    # Mock the connect_to_db function
    with patch("get_data_tpscore.upload_data") as mock_upload_data:
        with patch("substrateinterface.SubstrateInterface") as mock_substrateinterface:
            with patch("get_data_tpscore.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(2023, 8, 3, 12, 40, 56)
                ws_provider = mock_substrateinterface.return_value

                # Arrange
                chain_name = "Test Chain"
                endpoint = "wss://test.network.endpoint"

                class GenericExtrinsic:
                    def __init__(self, value):
                        self.value = value

                # Mock extrinsics with correct module names
                mock_extrinsics = [
                    GenericExtrinsic(
                        value={
                            "call": {
                                "call_module": "Timestamp",
                                "call_args": [
                                    {
                                        "name": "now",
                                        "type": "Moment",
                                        "value": 1691393586001,
                                    }
                                ],
                            }
                        }
                    ),
                    GenericExtrinsic(value={"call": {"call_module": "Balances"}}),
                ]

                ws_provider.get_block.return_value = {
                    "header": {"number": 1100},
                    "extrinsics": mock_extrinsics,
                }

                # Act
                get_data_tpscore.get_endpoint_chain_data(chain_name, endpoint)

                # Assert
                mock_substrateinterface.assert_called_once()
                ws_provider.get_block.assert_called()
                mock_datetime.utcfromtimestamp.assert_called()
                mock_upload_data.assert_called_once()
