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

### 방법 1: Colab 노트북 사용 (가장 쉬움) ⭐

1. Google Colab에서 `CryptoQuant_Data_Extractor.ipynb` 파일을 열기
2. 셀을 순서대로 실행
3. 데이터가 자동으로 CSV 파일로 다운로드됨

**Colab에서 직접 실행:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ym0179/coin_monitor/blob/claude/fix-highcharts-tooltip-01H4VypGM6KYkxLkzdAgoasy/CryptoQuant_Data_Extractor.ipynb)

### 방법 2: Colab에서 Python 스크립트 직접 실행

```python
# Colab 노트북의 새 셀에서 실행

# 1. 필요한 패키지 설치 (google-colab-selenium 사용)
!pip install -q google-colab-selenium pandas beautifulsoup4

# 2. 스크립트 다운로드
!wget -q https://raw.githubusercontent.com/ym0179/coin_monitor/claude/fix-highcharts-tooltip-01H4VypGM6KYkxLkzdAgoasy/cryptoquant_scraper.py

# 3. 데이터 추출
from cryptoquant_scraper import CryptoQuantScraper
import pandas as pd
from google.colab import files

url = "https://cryptoquant.com/asset/btc/chart/derivatives/open-interest?exchange=all_exchange&symbol=all_symbol&window=DAY"

scraper = CryptoQuantScraper(headless=True)
try:
    df = scraper.extract_highcharts_data(url)
    if df is not None:
        print(f"✅ {len(df)}개의 데이터 추출 완료!")
        print(df.tail())

        # CSV 저장 및 다운로드
        df.to_csv('btc_data.csv', index=False)
        files.download('btc_data.csv')
finally:
    scraper.close()
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

### 데이터 추출이 안 될 때 ⚠️

자동 스크래핑이 작동하지 않나요? **걱정하지 마세요!** 여러 해결 방법이 있습니다:

#### 1. 먼저 테스트 스크립트 실행

```bash
python test_extractor.py
```

이 스크립트가 어디서 문제가 발생하는지 알려줍니다.

#### 2. 수동 추출 방법 (100% 확실!) ⭐

브라우저에서 직접 데이터를 추출할 수 있습니다:

1. CryptoQuant 페이지를 브라우저에서 열기
2. F12를 눌러 개발자 도구 열기
3. Console 탭에서 [MANUAL_EXTRACTION.md](MANUAL_EXTRACTION.md)의 JavaScript 코드 실행
4. CSV 파일이 자동으로 다운로드됩니다!

**자세한 방법**: [MANUAL_EXTRACTION.md](MANUAL_EXTRACTION.md) 참고

#### 3. 대기 시간 늘리기

`cryptoquant_scraper.py`에서 대기 시간을 늘려보세요:

```python
wait_time = 20  # 10초에서 20초로 증가
```

#### 4. 헤드리스 모드 끄기 (디버깅용)

```python
scraper = CryptoQuantScraper(headless=False)
```

브라우저 창이 열려서 무슨 일이 일어나는지 볼 수 있습니다.

### Chrome 드라이버 오류 (해결됨!)

**이제 `google-colab-selenium`을 사용하므로 Chrome 드라이버 수동 설치가 필요 없습니다!**

단순히 다음 명령어만 실행하세요:

```bash
!pip install -q google-colab-selenium
```

스크래퍼가 자동으로 Colab 환경을 감지하고 올바른 드라이버를 사용합니다.

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
