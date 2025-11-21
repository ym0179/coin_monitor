"""
Test script for CryptoQuant data extractor
Tests if the scraper can successfully extract data
"""

from cryptoquant_scraper import CryptoQuantScraper
import pandas as pd


def test_extraction():
    """Test the data extraction"""

    print("=" * 80)
    print("CryptoQuant 데이터 추출 테스트")
    print("=" * 80)

    url = "https://cryptoquant.com/asset/btc/chart/derivatives/open-interest?exchange=all_exchange&symbol=all_symbol&window=DAY&sma=0&ema=0&priceScale=log&metricScale=linear&chartStyle=line"

    print(f"\nURL: {url}")
    print("\n테스트를 시작합니다...")
    print("(이 작업은 10-15초 정도 소요됩니다)\n")

    scraper = CryptoQuantScraper(headless=True)

    try:
        df = scraper.extract_highcharts_data(url)

        if df is not None and not df.empty:
            print("\n" + "=" * 80)
            print("✅ 성공! 데이터를 추출했습니다!")
            print("=" * 80)

            print(f"\n총 데이터 포인트: {len(df):,}개")
            print(f"컬럼: {', '.join(df.columns)}")

            # 날짜 범위
            if 'date' in df.columns:
                print(f"\n날짜 범위:")
                print(f"  시작: {df['date'].min()}")
                print(f"  종료: {df['date'].max()}")

            # 최신 데이터
            print(f"\n최신 데이터:")
            print("-" * 80)
            latest = df.iloc[-1]
            for col in df.columns:
                value = latest[col]
                if isinstance(value, float):
                    print(f"  {col}: {value:,.2f}")
                else:
                    print(f"  {col}: {value}")

            # 데이터 미리보기
            print(f"\n데이터 미리보기 (처음 5개):")
            print("-" * 80)
            print(df.head().to_string())

            # CSV 저장
            filename = 'test_cryptoquant_data.csv'
            df.to_csv(filename, index=False)
            print(f"\n✅ 데이터가 '{filename}' 파일로 저장되었습니다.")

            return True

        else:
            print("\n" + "=" * 80)
            print("❌ 실패: 데이터를 추출하지 못했습니다")
            print("=" * 80)

            print("\n다음 방법을 시도해보세요:")
            print("\n1. 수동 추출 방법:")
            print("   MANUAL_EXTRACTION.md 파일을 참고하세요")

            print("\n2. 대기 시간 늘리기:")
            print("   cryptoquant_scraper.py에서 wait_time 값을 늘려보세요")
            print("   (현재: Colab 15초, 로컬 10초)")

            print("\n3. 헤드리스 모드 끄기:")
            print("   CryptoQuantScraper(headless=False)로 실행하여")
            print("   브라우저에서 무슨 일이 일어나는지 확인하세요")

            print("\n4. 브라우저 콘솔에서 직접 확인:")
            print("   1) CryptoQuant 페이지를 브라우저에서 열기")
            print("   2) F12를 눌러 개발자 도구 열기")
            print("   3) Console 탭에서 다음 명령어 실행:")
            print("      typeof Highcharts")
            print("      Highcharts.charts")

            return False

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 오류 발생: {e}")
        print("=" * 80)

        import traceback
        print("\n상세 오류:")
        traceback.print_exc()

        return False

    finally:
        scraper.close()
        print("\n" + "=" * 80)
        print("테스트 종료")
        print("=" * 80)


if __name__ == "__main__":
    success = test_extraction()

    if not success:
        print("\n💡 Tip: MANUAL_EXTRACTION.md 파일에서 수동 추출 방법을 확인하세요!")

    exit(0 if success else 1)
