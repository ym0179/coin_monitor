"""
CryptoQuant API Data Extractor
Alternative method using direct API calls (if available)

Note: This script attempts to call CryptoQuant's backend API.
You may need to inspect the network tab in browser developer tools
to find the exact API endpoints and required headers/parameters.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json


class CryptoQuantAPI:
    def __init__(self, api_key=None):
        """
        Initialize the API client

        Args:
            api_key (str, optional): CryptoQuant API key if required
        """
        self.base_url = "https://api.cryptoquant.com"
        self.api_key = api_key
        self.session = requests.Session()

        # Set common headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })

    def get_open_interest_and_price(self,
                                    asset='btc',
                                    exchange='all_exchange',
                                    symbol='all_symbol',
                                    window='DAY',
                                    start_date=None,
                                    end_date=None):
        """
        Fetch open interest and price data

        Args:
            asset (str): Asset symbol (default: 'btc')
            exchange (str): Exchange name (default: 'all_exchange')
            symbol (str): Symbol (default: 'all_symbol')
            window (str): Time window (default: 'DAY')
            start_date (datetime, optional): Start date
            end_date (datetime, optional): End date

        Returns:
            pd.DataFrame: Data with date, price, and open interest
        """

        # This is a placeholder endpoint - you need to inspect the actual API calls
        # in your browser's Network tab when visiting the CryptoQuant page
        endpoint = f"/v1/btc/open-interest"

        params = {
            'exchange': exchange,
            'symbol': symbol,
            'window': window,
        }

        if start_date:
            params['from'] = int(start_date.timestamp())
        if end_date:
            params['to'] = int(end_date.timestamp())

        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()

            data = response.json()
            return self._process_api_data(data)

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            print("\nNote: You may need to:")
            print("1. Check the actual API endpoint in browser developer tools (Network tab)")
            print("2. Obtain an API key from CryptoQuant")
            print("3. Update the endpoint and parameters in this script")
            return None

    def _process_api_data(self, data):
        """
        Process API response data into DataFrame

        Args:
            data: Raw API response

        Returns:
            pd.DataFrame: Processed data
        """
        # This processing logic depends on the actual API response format
        # Adjust based on the real response structure

        if isinstance(data, dict) and 'result' in data:
            df = pd.DataFrame(data['result'])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])

        # Convert timestamp to datetime if present
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        return df


def get_data_with_browser_inspection():
    """
    Instructions for manually inspecting browser network calls
    """
    instructions = """
    To find the actual API endpoint:

    1. Open the CryptoQuant page in your browser:
       https://cryptoquant.com/asset/btc/chart/derivatives/open-interest

    2. Open Developer Tools (F12)

    3. Go to the Network tab

    4. Refresh the page or hover over chart points

    5. Look for XHR/Fetch requests that return JSON data

    6. Click on the request to see:
       - Request URL (the API endpoint)
       - Request Headers (authentication, user-agent, etc.)
       - Query Parameters
       - Response data format

    7. Copy the Request URL and headers

    8. Update this script with the correct endpoint and parameters

    Example of what you might find:
    - Endpoint: https://api.cryptoquant.com/v1/btc/market-data/open-interest
    - Headers: Authorization, API-Key, etc.
    - Params: from, to, interval, exchange, etc.
    """
    print(instructions)


if __name__ == "__main__":
    # Show instructions for finding API endpoint
    get_data_with_browser_inspection()

    # Example usage (will likely fail without correct endpoint):
    # api = CryptoQuantAPI(api_key='your_api_key_here')
    # df = api.get_open_interest_and_price()
    # if df is not None:
    #     print(df.head())
    #     df.to_csv('cryptoquant_api_data.csv', index=False)
