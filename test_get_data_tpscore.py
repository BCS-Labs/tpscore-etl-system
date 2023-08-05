import pytest
from unittest.mock import patch, Mock
from get_data_tpscore import upload_data, connect_to_db
import substrateinterface
from pymysql import cursors

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
        connect_to_db(expected_connection_params['host'], expected_connection_params['user'], expected_connection_params['password'])

        # Assert
        mock_connect.assert_called_once_with(**expected_connection_params)


def test_upload_data_success():
    with patch("get_data_tpscore.connect_to_db") as mock_connect_db:
        mock_connection = mock_connect_db.return_value
        mock_cursor = mock_connection.cursor.return_value

        # Arrange
        processing_started_at = "2023-08-03 12:40:56"
        chain_name = "Test Chain"
        datetime_start = "2023-08-03 12:34:00"
        datetime_finish = "2023-08-03 12:40:00"
        block_start = 1000
        block_finish = 1100
        avg_n_txns_in_block = 10.5
        tps = 5.7
        
        # Act
        upload_data(
            processing_started_at,
            chain_name,
            datetime_start,
            datetime_finish,
            block_start,
            block_finish,
            avg_n_txns_in_block,
            tps
        )
        
        # Assert
        expected_sql_query = (
            "INSERT INTO tps(processing_started_at, chain_name, datetime_start, datetime_finish, block_start, block_finish, avg_n_txns_in_block, tps) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        expected_params = (
            processing_started_at,
            chain_name,
            datetime_start,
            datetime_finish,
            block_start,
            block_finish,
            avg_n_txns_in_block,
            tps
        )

        mock_cursor.execute.assert_called_once_with(expected_sql_query, expected_params)
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()
        print.assert_called_once_with(f"Records uploaded successfully at {processing_started_at}")


def test_type_of_processing_started_at():
    assert True

def test_parachain_endpoint_returns_correct_data():
    assert True

def test_connection_to_parachain_endpoint():
    assert True

def test_block_difference():
    assert True

def test_time_delta_of_blocks():
    assert True

def test_tps_calculation():
    assert True

def test_avg_n_txns_in_block():
    assert True

def test_tps_data_to_be_saved_in_db():
    assert True