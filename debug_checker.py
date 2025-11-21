"""
디버그용 간단한 스크립트
CryptoQuant 페이지에서 무엇을 볼 수 있는지 확인
"""

try:
    import google.colab
    IN_COLAB = True
    import google_colab_selenium as gs
    print("✅ Colab 환경")
except ImportError:
    IN_COLAB = False
    from selenium import webdriver
    print("✅ 로컬 환경")

from selenium.webdriver.chrome.options import Options
import time

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

# 드라이버 시작
if IN_COLAB:
    driver = gs.Chrome(options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

url = "https://cryptoquant.com/asset/btc/chart/derivatives/open-interest?exchange=all_exchange&symbol=all_symbol&window=DAY"

print(f"\n페이지 로딩: {url}")
driver.get(url)

# 여러 시간대에 확인
for wait_time in [5, 10, 15, 20]:
    print(f"\n{'='*60}")
    print(f"{wait_time}초 대기 후 확인...")
    print('='*60)

    time.sleep(5)  # 5초씩 증가

    # JavaScript로 페이지 상태 확인
    info = driver.execute_script("""
        return {
            title: document.title,
            url: window.location.href,
            bodyLength: document.body ? document.body.innerText.length : 0,
            highchartsExists: typeof Highcharts !== 'undefined',
            highchartsVersion: typeof Highcharts !== 'undefined' ? Highcharts.version : 'N/A',
            chartsCount: typeof Highcharts !== 'undefined' && Highcharts.charts ?
                Highcharts.charts.filter(c => c !== undefined).length : 0,
            windowKeys: Object.keys(window).filter(k => k.toLowerCase().includes('chart')).slice(0, 10),
            scriptTags: document.querySelectorAll('script').length,
            hasIframe: document.querySelectorAll('iframe').length,
            bodyText: document.body ? document.body.innerText.substring(0, 300) : ''
        };
    """)

    print(f"페이지 제목: {info['title']}")
    print(f"URL: {info['url'][:80]}...")
    print(f"본문 길이: {info['bodyLength']} 문자")
    print(f"Script 태그 수: {info['scriptTags']}")
    print(f"Iframe 수: {info['hasIframe']}")
    print(f"\nHighcharts 존재: {info['highchartsExists']}")

    if info['highchartsExists']:
        print(f"✅ Highcharts 버전: {info['highchartsVersion']}")
        print(f"✅ 차트 개수: {info['chartsCount']}")

        # 차트 데이터 확인
        if info['chartsCount'] > 0:
            chart_info = driver.execute_script("""
                let charts = Highcharts.charts.filter(c => c !== undefined);
                return charts.map(chart => ({
                    seriesCount: chart.series ? chart.series.length : 0,
                    seriesNames: chart.series ? chart.series.map(s => s.name) : [],
                    dataPoints: chart.series ? chart.series.map(s => s.data ? s.data.length : 0) : []
                }));
            """)

            print(f"\n차트 상세 정보:")
            for i, chart in enumerate(chart_info):
                print(f"  차트 {i+1}:")
                print(f"    시리즈 개수: {chart['seriesCount']}")
                print(f"    시리즈 이름: {chart['seriesNames']}")
                print(f"    데이터 포인트: {chart['dataPoints']}")

            print("\n✅✅✅ 데이터를 찾았습니다! ✅✅✅")
            break
        else:
            print("⚠️ Highcharts는 있지만 차트가 비어있습니다")
    else:
        print("❌ Highcharts를 찾을 수 없습니다")
        print(f"Window 객체의 chart 관련 키: {info['windowKeys']}")

    print(f"\n페이지 내용 (처음 300자):")
    print(info['bodyText'][:300])

print(f"\n{'='*60}")
print("테스트 완료")
print('='*60)

driver.quit()
