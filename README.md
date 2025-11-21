# CryptoQuant 데이터 추출기

CryptoQuant에서 BTC 가격과 미결제 약정(Open Interest) 데이터를 추출하는 도구입니다.

## 추출 가능한 데이터

- **날짜** (Date)
- **BTC 가격** (Price USD): 84,578.75233399
- **미결제 약정** (Open Interest): 30,369,888,176.964546

## 파일 설명

1. **CryptoQuant_Data_Extractor.ipynb** - Google Colab에서 바로 사용 가능한 노트북 (추천)
2. **cryptoquant_scraper.py** - Selenium 기반 스크래핑 스크립트
3. **cryptoquant_api.py** - API 직접 호출 방법 (참고용)
4. **requirements.txt** - 필요한 Python 패키지 목록

## 빠른 시작 (Google Colab - 추천)

### 방법 1: Colab 노트북 사용 (가장 쉬움)

1. Google Colab에서 `CryptoQuant_Data_Extractor.ipynb` 파일을 열기
2. 셀을 순서대로 실행
3. 데이터가 자동으로 CSV 파일로 다운로드됨

**Colab에서 직접 실행:**

```python
# 1. GitHub에서 노트북 다운로드 (또는 직접 업로드)
!wget https://raw.githubusercontent.com/your-repo/coin_monitor/main/CryptoQuant_Data_Extractor.ipynb

# 2. Colab에서 노트북을 열고 실행
```

### 방법 2: Colab에서 Python 스크립트 직접 실행

```python
# Colab 노트북의 새 셀에서 실행

# 1. 필요한 패키지 설치
!pip install selenium pandas webdriver-manager -q

# 2. Chrome 설정
!apt-get update
!apt install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

# 3. 스크립트 다운로드 및 실행
!wget https://raw.githubusercontent.com/your-repo/coin_monitor/main/cryptoquant_scraper.py
!python cryptoquant_scraper.py

# 4. 결과 확인
import pandas as pd
df = pd.read_csv('cryptoquant_data.csv')
print(df.head())
```

## 로컬 환경에서 실행

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-repo/coin_monitor.git
cd coin_monitor

# 패키지 설치
pip install -r requirements.txt
```

### 사용법

```bash
# 기본 실행
python cryptoquant_scraper.py
```

### Python 코드에서 사용

```python
from cryptoquant_scraper import CryptoQuantScraper

# 스크래퍼 초기화
scraper = CryptoQuantScraper(headless=True)

try:
    # 데이터 추출
    url = "https://cryptoquant.com/asset/btc/chart/derivatives/open-interest"
    df = scraper.extract_highcharts_data(url)

    # 데이터 확인
    print(df.head())

    # CSV로 저장
    df.to_csv('btc_data.csv', index=False)

finally:
    scraper.close()
```

## 출력 데이터 형식

CSV 파일은 다음과 같은 컬럼을 포함합니다:

| 컬럼 | 설명 | 예시 |
|------|------|------|
| date | 날짜 | 2025-11-21 |
| timestamp | Unix 타임스탬프 | 1732147200000 |
| price_usd | BTC 가격 (USD) | 84578.75233399 |
| open_interest | 미결제 약정 | 30369888176.964546 |

## 고급 사용법

### 특정 기간 데이터만 필터링

```python
import pandas as pd

df = pd.read_csv('cryptoquant_data.csv')
df['date'] = pd.to_datetime(df['date'])

# 2025년 이후 데이터만
df_2025 = df[df['date'] >= '2025-01-01']

# 최근 30일 데이터
df_recent = df.tail(30)
```

### 데이터 시각화

```python
import matplotlib.pyplot as plt

df = pd.read_csv('cryptoquant_data.csv')
df['date'] = pd.to_datetime(df['date'])

# 가격 그래프
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['price_usd'])
plt.title('BTC Price Over Time')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 미결제 약정 그래프
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['open_interest'])
plt.title('BTC Open Interest Over Time')
plt.xlabel('Date')
plt.ylabel('Open Interest')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## 문제 해결

### Chrome 드라이버 오류

Colab에서 Chrome 드라이버 오류가 발생하면:

```bash
!apt-get update
!apt install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
```

### 데이터를 찾을 수 없음

- 페이지 로딩 시간을 늘려보세요 (time.sleep 값 증가)
- 헤드리스 모드를 끄고 브라우저를 확인해보세요: `CryptoQuantScraper(headless=False)`

### API 직접 호출하기

API 엔드포인트를 찾으려면:

1. CryptoQuant 페이지를 브라우저에서 열기
2. 개발자 도구 (F12) → Network 탭 열기
3. 페이지 새로고침 또는 차트 위에 마우스 올리기
4. XHR/Fetch 요청 확인
5. 응답이 JSON인 요청 찾기
6. `cryptoquant_api.py`에서 해당 엔드포인트 사용

## 주의사항

- CryptoQuant의 이용약관을 준수하세요
- 과도한 요청은 IP 차단을 유발할 수 있습니다
- 상업적 사용 시 CryptoQuant API 라이센스를 확인하세요
- 데이터는 교육 및 개인 연구 목적으로만 사용하세요

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.

## 기여

이슈나 풀 리퀘스트를 환영합니다!

## 관련 링크

- [CryptoQuant](https://cryptoquant.com/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
