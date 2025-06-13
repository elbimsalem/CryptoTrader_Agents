# src/crypto_trader/tests/test_tools.py

import pytest
import requests
from unittest.mock import patch, MagicMock

from crypto_trader.tools.binance_rapidapi_tool import BinanceRapidApiTool

@pytest.fixture
def tool():
    """Provides a BinanceRapidApiTool instance for testing."""
    # We patch the environment variables to ensure the tool can be initialized
    # without needing a real .env file during tests.
    with patch.dict('os.environ', {'RAPIDAPI_KEY': 'test_key', 'RAPIDAPI_BINANCE_HOST': 'test_host'}):
        yield BinanceRapidApiTool()

@patch('requests.get')
def test_get_kline_data_success(mock_get, tool):
    """Tests the successful retrieval of Kline (candlestick) data."""
    # --- Arrange ---
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        [1672531200000, "40000.0", "40100.0", "39900.0", "40050.0", "1000", 1672534799999]
    ]
    mock_get.return_value = mock_response

    # --- Act ---
    params = {'symbol': 'BTCUSDT', 'interval': '1h', 'limit': 1}
    result = tool._run(action='get_kline_data', parameters=params)

    # --- Assert ---
    mock_get.assert_called_once()
    assert '1672531200000' in result
    assert '"40000.0"' in result

@patch('requests.get')
def test_get_kline_data_http_error(mock_get, tool):
    """Tests how the tool handles an HTTP error from the API."""
    # --- Arrange ---
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_get.return_value = mock_response

    # --- Act ---
    params = {'symbol': 'BTCUSDT', 'interval': '1h'}
    result = tool._run(action='get_kline_data', parameters=params)

    # --- Assert ---
    assert "HTTP Error: 404" in result
    assert "Not Found" in result

def test_invalid_action(tool):
    """Tests the tool's response to an unknown action."""
    # --- Act ---
    result = tool._run(action='non_existent_action', parameters={})

    # --- Assert ---
    assert "Error: Invalid action 'non_existent_action' specified." in result

def test_missing_parameters(tool):
    """Tests the tool's response when required parameters are missing."""
    # --- Act ---
    result = tool._run(action='get_kline_data', parameters={'interval': '1h'}) # Missing 'symbol'

    # --- Assert ---
    assert "Error processing 'get_kline_data'" in result
    # **FINAL FIX**: Check for Pydantic's specific message for missing fields.
    assert "Field required" in result