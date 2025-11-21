# 수동 데이터 추출 방법

자동 스크래핑이 작동하지 않을 때 브라우저에서 직접 데이터를 추출하는 방법입니다.

## 방법 1: 브라우저 콘솔에서 직접 추출 (가장 확실!)

### 단계

1. **CryptoQuant 페이지 열기**
   ```
   https://cryptoquant.com/asset/btc/chart/derivatives/open-interest?exchange=all_exchange&symbol=all_symbol&window=DAY
   ```

2. **개발자 도구 열기**
   - Windows/Linux: `F12` 또는 `Ctrl + Shift + I`
   - Mac: `Cmd + Option + I`

3. **Console 탭으로 이동**

4. **다음 코드를 복사해서 콘솔에 붙여넣고 Enter**

```javascript
// CryptoQuant 데이터 추출 스크립트
(function() {
    console.log('🔍 데이터 추출 시작...');

    // Highcharts에서 데이터 추출
    if (typeof Highcharts !== 'undefined' && Highcharts.charts) {
        let allData = [];

        Highcharts.charts.forEach((chart, chartIndex) => {
            if (chart && chart.series) {
                console.log(`📊 차트 ${chartIndex + 1}: ${chart.series.length}개 시리즈 발견`);

                chart.series.forEach((series, seriesIndex) => {
                    if (series && series.data && series.name) {
                        console.log(`  - ${series.name}: ${series.data.length}개 데이터 포인트`);

                        series.data.forEach(point => {
                            const date = new Date(point.x);
                            const dateStr = date.toISOString().split('T')[0];

                            allData.push({
                                date: dateStr,
                                series: series.name,
                                value: point.y
                            });
                        });
                    }
                });
            }
        });

        if (allData.length > 0) {
            console.log(`✅ 총 ${allData.length}개의 데이터 포인트 추출!`);

            // CSV 형식으로 변환
            let csv = 'date,series,value\\n';
            allData.forEach(row => {
                csv += `${row.date},${row.series},${row.value}\\n`;
            });

            // CSV 다운로드
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cryptoquant_data.csv';
            a.click();

            console.log('✅ CSV 파일 다운로드 시작!');

            // 데이터 미리보기
            console.table(allData.slice(0, 10));

        } else {
            console.log('❌ 데이터를 찾을 수 없습니다.');
        }
    } else {
        console.log('❌ Highcharts를 찾을 수 없습니다.');
    }
})();
```

5. **CSV 파일이 자동으로 다운로드됩니다!**

---

## 방법 2: 네트워크 탭에서 API 요청 찾기

### 단계

1. **개발자 도구 열기** (F12)

2. **Network 탭으로 이동**

3. **필터를 "XHR" 또는 "Fetch"로 설정**

4. **페이지 새로고침** (F5)

5. **API 호출 찾기**
   - `api`, `chart`, `data` 등이 포함된 요청 찾기
   - 응답이 JSON 형식인 요청 확인

6. **요청 URL 복사**
   - 마우스 우클릭 → "Copy" → "Copy URL"

7. **요청 헤더 확인**
   - Headers 탭에서 필요한 헤더 확인
   - Cookie, Authorization 등

8. **Python으로 직접 요청**

```python
import requests
import pandas as pd

# 복사한 URL
url = "복사한_API_URL"

# 필요한 헤더 (브라우저에서 복사)
headers = {
    'User-Agent': 'Mozilla/5.0 ...',
    'Authorization': 'Bearer ...',  # 필요한 경우
}

# 요청
response = requests.get(url, headers=headers)
data = response.json()

# DataFrame으로 변환
df = pd.DataFrame(data)
df.to_csv('cryptoquant_data.csv', index=False)
```

---

## 방법 3: 간단한 데이터 복사

### 단계

1. **차트 위에 마우스를 올리면 툴팁에 데이터가 표시됩니다**

2. **브라우저 콘솔에서 툴팁 데이터 수집**

```javascript
// 차트의 모든 포인트를 순회하며 데이터 수집
let data = [];
let chart = Highcharts.charts[0];  // 첫 번째 차트

if (chart) {
    chart.series.forEach(series => {
        series.data.forEach(point => {
            data.push({
                date: new Date(point.x).toISOString().split('T')[0],
                [series.name]: point.y
            });
        });
    });
}

console.table(data);
copy(JSON.stringify(data));  // 클립보드에 복사
```

---

## 방법 4: 스크린샷 및 OCR (최후의 수단)

만약 위의 모든 방법이 실패한다면:

1. 차트의 여러 부분에 마우스를 올려 데이터 기록
2. 스크린샷 촬영
3. OCR 도구 사용 (예: Google Vision API)

---

## 문제 해결

### "Highcharts is not defined" 오류

차트가 완전히 로드되기 전에 스크립트를 실행했을 수 있습니다.

**해결책**: 몇 초 기다린 후 다시 시도

```javascript
setTimeout(() => {
    // 위의 추출 코드를 여기에 붙여넣기
}, 5000);  // 5초 대기
```

### 데이터가 비어있음

사이트에 로그인이 필요할 수 있습니다.

**해결책**:
1. CryptoQuant에 로그인
2. 다시 시도

### CSV 다운로드가 안됨

브라우저가 팝업을 차단했을 수 있습니다.

**해결책**:
1. 브라우저 주소창의 팝업 차단 아이콘 클릭
2. 팝업 허용
3. 스크립트 다시 실행

---

## 추출한 데이터 사용하기

### Python에서 CSV 읽기

```python
import pandas as pd

# CSV 읽기
df = pd.read_csv('cryptoquant_data.csv')

# 데이터 확인
print(df.head())

# Pivot하여 날짜별로 정리
df_pivot = df.pivot(index='date', columns='series', values='value')
print(df_pivot.head())

# 저장
df_pivot.to_csv('cryptoquant_clean.csv')
```

### Google Colab에서 사용

```python
# Colab에서 파일 업로드
from google.colab import files
uploaded = files.upload()

# 데이터 읽기
import pandas as pd
df = pd.read_csv('cryptoquant_data.csv')

# 분석 시작!
```

---

## 도움이 필요하면

- GitHub Issues: [coin_monitor/issues](https://github.com/ym0179/coin_monitor/issues)
- 디버그 정보를 포함해주세요:
  - 브라우저 버전
  - 콘솔 오류 메시지
  - 실행한 코드
