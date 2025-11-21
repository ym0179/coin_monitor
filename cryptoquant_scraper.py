"""
CryptoQuant BTC Open Interest and Price Data Scraper
Extracts data from CryptoQuant charts using Selenium
Supports both Google Colab and local environments
"""

import time
import json
import pandas as pd
from datetime import datetime

# Try to detect Colab environment and import appropriate selenium
try:
    import google.colab
    IN_COLAB = True
    import google_colab_selenium as gs
    print("✅ Google Colab 환경 감지 - google-colab-selenium 사용")
except ImportError:
    IN_COLAB = False
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("✅ 로컬 환경 감지 - 일반 selenium 사용")

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class CryptoQuantScraper:
    def __init__(self, headless=True):
        """
        Initialize the scraper with Chrome options

        Args:
            headless (bool): Run browser in headless mode (Colab에서는 무시됨)
        """
        self.chrome_options = Options()
        if headless and not IN_COLAB:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--disable-infobars')
        self.driver = None
        self.is_colab = IN_COLAB

    def start_driver(self):
        """Start the Chrome WebDriver"""
        if self.is_colab:
            # Google Colab 환경
            print("Google Colab에서 Chrome 드라이버 시작...")
            self.driver = gs.Chrome(options=self.chrome_options)
        else:
            # 로컬 환경
            print("로컬 환경에서 Chrome 드라이버 시작...")
            self.driver = webdriver.Chrome(options=self.chrome_options)

    def extract_highcharts_data(self, url):
        """
        Extract data from Highcharts chart

        Args:
            url (str): CryptoQuant chart URL

        Returns:
            pd.DataFrame: DataFrame with date, price, and open interest
        """
        if not self.driver:
            self.start_driver()

        print(f"Loading URL: {url}")
        self.driver.get(url)

        # Wait for chart to load (longer wait for Colab)
        wait_time = 8 if self.is_colab else 5
        print(f"Waiting for chart to load ({wait_time} seconds)...")
        time.sleep(wait_time)

        # Extract Highcharts data from JavaScript
        script = """
        try {
            // Get all Highcharts instances
            if (typeof Highcharts !== 'undefined' && Highcharts.charts) {
                let allData = [];

                // Loop through all chart instances
                for (let chart of Highcharts.charts) {
                    if (chart && chart.series) {
                        let chartData = {
                            series: []
                        };

                        // Extract data from each series
                        chart.series.forEach((series, index) => {
                            if (series && series.data && series.name) {
                                let seriesData = {
                                    name: series.name,
                                    data: series.data.map(point => ({
                                        x: point.x,
                                        y: point.y,
                                        date: new Date(point.x).toISOString()
                                    }))
                                };
                                chartData.series.push(seriesData);
                            }
                        });

                        allData.push(chartData);
                    }
                }

                return JSON.stringify(allData);
            }
            return null;
        } catch (e) {
            return JSON.stringify({error: e.toString()});
        }
        """

        print("Extracting chart data...")
        result = self.driver.execute_script(script)

        if result:
            data = json.loads(result)
            print(f"Extracted data: {len(data)} chart(s) found")
            return self._process_data(data)
        else:
            print("No Highcharts data found")
            return None

    def _process_data(self, raw_data):
        """
        Process raw Highcharts data into a structured DataFrame

        Args:
            raw_data: Raw data from Highcharts

        Returns:
            pd.DataFrame: Processed data
        """
        if not raw_data or len(raw_data) == 0:
            return None

        all_records = []

        for chart in raw_data:
            if 'series' not in chart:
                continue

            # Create a mapping of dates to values
            date_map = {}

            for series in chart['series']:
                series_name = series['name']
                print(f"Processing series: {series_name}")

                for point in series['data']:
                    date = point['date']
                    if date not in date_map:
                        date_map[date] = {
                            'date': date,
                            'timestamp': point['x']
                        }

                    # Map series names to column names
                    if 'price' in series_name.lower() or 'usd' in series_name.lower():
                        date_map[date]['price_usd'] = point['y']
                    elif 'open interest' in series_name.lower():
                        date_map[date]['open_interest'] = point['y']
                    else:
                        # Use the series name as column name
                        date_map[date][series_name.lower().replace(' ', '_')] = point['y']

            # Convert to list of records
            all_records.extend(date_map.values())

        if not all_records:
            return None

        # Create DataFrame
        df = pd.DataFrame(all_records)

        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date')
            df['date'] = pd.to_datetime(df['date'])

        return df

    def save_to_csv(self, df, filename='cryptoquant_data.csv'):
        """
        Save DataFrame to CSV file

        Args:
            df (pd.DataFrame): Data to save
            filename (str): Output filename
        """
        if df is not None and not df.empty:
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
            print(f"Total records: {len(df)}")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst few rows:")
            print(df.head())
        else:
            print("No data to save")

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()


def main():
    """Main function to run the scraper"""

    # CryptoQuant URL
    url = "https://cryptoquant.com/asset/btc/chart/derivatives/open-interest?exchange=all_exchange&symbol=all_symbol&window=DAY&sma=0&ema=0&priceScale=log&metricScale=linear&chartStyle=line"

    # Initialize scraper
    scraper = CryptoQuantScraper(headless=True)

    try:
        # Extract data
        df = scraper.extract_highcharts_data(url)

        # Save to CSV
        scraper.save_to_csv(df)

    finally:
        # Clean up
        scraper.close()


if __name__ == "__main__":
    main()
