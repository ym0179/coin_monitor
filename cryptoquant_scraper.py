"""
CryptoQuant BTC Open Interest and Price Data Scraper
Extracts data from CryptoQuant charts using Selenium
Supports both Google Colab and local environments
Uses network request interception for reliable data extraction
"""

import time
import json
import pandas as pd
from datetime import datetime
import re

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

        # Enable performance logging to capture network requests
        if not IN_COLAB:
            self.chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        self.driver = None
        self.is_colab = IN_COLAB
        self.api_data = None

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

    def extract_network_data(self):
        """
        Extract data from network requests (for local environment)
        """
        if self.is_colab:
            return None

        try:
            logs = self.driver.get_log('performance')

            for log in logs:
                try:
                    message = json.loads(log['message'])['message']

                    # Look for Network.responseReceived events
                    if message['method'] == 'Network.responseReceived':
                        response = message['params']['response']
                        url = response['url']

                        # Check if this is an API call for chart data
                        if 'api' in url.lower() or 'chart' in url.lower() or 'data' in url.lower():
                            print(f"Found API call: {url}")

                            # Try to get response body
                            try:
                                request_id = message['params']['requestId']
                                response_body = self.driver.execute_cdp_cmd(
                                    'Network.getResponseBody',
                                    {'requestId': request_id}
                                )
                                if response_body:
                                    return json.loads(response_body['body'])
                            except:
                                continue
                except:
                    continue

        except Exception as e:
            print(f"Network extraction error: {e}")

        return None

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

        # Wait for chart to load (longer wait for Colab and initial load)
        wait_time = 15 if self.is_colab else 10
        print(f"Waiting for chart to load ({wait_time} seconds)...")
        time.sleep(wait_time)

        # Try multiple extraction methods
        print("\n=== 방법 1: Highcharts 객체에서 데이터 추출 ===")
        df = self._extract_from_highcharts()

        if df is not None and not df.empty:
            return df

        print("\n=== 방법 2: 페이지 소스에서 데이터 찾기 ===")
        df = self._extract_from_page_source()

        if df is not None and not df.empty:
            return df

        if not self.is_colab:
            print("\n=== 방법 3: 네트워크 요청 캡처 ===")
            network_data = self.extract_network_data()
            if network_data:
                df = self._process_network_data(network_data)
                if df is not None and not df.empty:
                    return df

        print("\n❌ 모든 방법으로 데이터를 추출하지 못했습니다.")
        print("디버깅 정보:")
        self._print_debug_info()

        return None

    def _extract_from_highcharts(self):
        """Extract data directly from Highcharts object"""
        script = """
        try {
            if (typeof Highcharts !== 'undefined' && Highcharts.charts) {
                let allData = [];
                console.log('Highcharts charts found:', Highcharts.charts.length);

                for (let chart of Highcharts.charts) {
                    if (chart && chart.series) {
                        console.log('Chart found with', chart.series.length, 'series');
                        let chartData = { series: [] };

                        chart.series.forEach((series, index) => {
                            if (series && series.data && series.name) {
                                console.log('Series:', series.name, 'Points:', series.data.length);
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

                        if (chartData.series.length > 0) {
                            allData.push(chartData);
                        }
                    }
                }

                return JSON.stringify(allData);
            }
            return JSON.stringify({error: 'Highcharts not found'});
        } catch (e) {
            return JSON.stringify({error: e.toString()});
        }
        """

        try:
            result = self.driver.execute_script(script)

            if result:
                data = json.loads(result)

                if isinstance(data, dict) and 'error' in data:
                    print(f"  ⚠️ {data['error']}")
                    return None

                if isinstance(data, list) and len(data) > 0:
                    print(f"  ✅ {len(data)}개의 차트 발견")
                    return self._process_data(data)
                else:
                    print("  ⚠️ 차트 데이터가 비어있습니다")

        except Exception as e:
            print(f"  ❌ 오류: {e}")

        return None

    def _extract_from_page_source(self):
        """Extract data from page source (embedded JSON)"""
        try:
            page_source = self.driver.page_source

            # Look for JSON data in script tags
            json_pattern = r'<script[^>]*>.*?(\{.*?"data":\s*\[.*?\].*?\}).*?</script>'
            matches = re.findall(json_pattern, page_source, re.DOTALL)

            for match in matches:
                try:
                    data = json.loads(match)
                    if 'data' in data or 'series' in data:
                        print(f"  ✅ JSON 데이터 발견")
                        return self._process_json_data(data)
                except:
                    continue

            print("  ⚠️ 페이지 소스에서 데이터를 찾지 못했습니다")

        except Exception as e:
            print(f"  ❌ 오류: {e}")

        return None

    def _process_network_data(self, data):
        """Process data from network requests"""
        try:
            # This would process API response data
            # Implementation depends on actual API response format
            print("  Processing network data...")
            return self._process_json_data(data)
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            return None

    def _process_json_data(self, data):
        """Process generic JSON data"""
        # Implementation depends on actual data structure
        # This is a placeholder
        return None

    def _print_debug_info(self):
        """Print debugging information"""
        try:
            # Check if Highcharts is loaded
            script = """
            return {
                highchartsLoaded: typeof Highcharts !== 'undefined',
                chartsCount: typeof Highcharts !== 'undefined' && Highcharts.charts ? Highcharts.charts.length : 0,
                pageTitle: document.title,
                bodyText: document.body ? document.body.innerText.substring(0, 200) : 'No body'
            };
            """
            info = self.driver.execute_script(script)
            print(f"  - Highcharts 로드됨: {info.get('highchartsLoaded', False)}")
            print(f"  - 차트 개수: {info.get('chartsCount', 0)}")
            print(f"  - 페이지 제목: {info.get('pageTitle', 'Unknown')}")
            print(f"  - 페이지 내용 (일부): {info.get('bodyText', '')[:100]}...")

        except Exception as e:
            print(f"  디버그 정보 출력 오류: {e}")

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
                print(f"  Processing series: {series_name} ({len(series['data'])} points)")

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
            print(f"\n✅ Data saved to {filename}")
            print(f"Total records: {len(df)}")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst few rows:")
            print(df.head())
        else:
            print("\n❌ No data to save")

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
