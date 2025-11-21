"""
Quick extraction script for CryptoQuant data
간단하게 데이터를 추출하는 스크립트
"""

from cryptoquant_scraper import CryptoQuantScraper
import pandas as pd


def main():
    """
    BTC 가격과 미결제 약정 데이터를 빠르게 추출
    """
    print("=" * 60)
    print("CryptoQuant BTC 데이터 추출 시작")
    print("=" * 60)

    # CryptoQuant URL
    url = "https://cryptoquant.com/asset/btc/chart/derivatives/open-interest?exchange=all_exchange&symbol=all_symbol&window=DAY&sma=0&ema=0&priceScale=log&metricScale=linear&chartStyle=line"

    # 스크래퍼 초기화
    scraper = CryptoQuantScraper(headless=True)

    try:
        # 데이터 추출
        print("\n데이터를 추출하는 중...")
        df = scraper.extract_highcharts_data(url)

        if df is not None and not df.empty:
            # CSV 저장
            filename = 'cryptoquant_btc_data.csv'
            df.to_csv(filename, index=False)

            print("\n" + "=" * 60)
            print("✓ 데이터 추출 완료!")
            print("=" * 60)
            print(f"\n파일: {filename}")
            print(f"총 데이터 수: {len(df)}개")
            print(f"컬럼: {', '.join(df.columns)}")

            # 최근 데이터 표시
            if not df.empty:
                print("\n" + "-" * 60)
                print("최신 데이터:")
                print("-" * 60)

                latest = df.iloc[-1]
                print(f"날짜: {latest['date']}")

                if 'price_usd' in df.columns:
                    print(f"BTC 가격: ${latest['price_usd']:,.2f}")

                if 'open_interest' in df.columns:
                    print(f"미결제 약정: ${latest['open_interest']:,.2f}")

            # 데이터 미리보기
            print("\n" + "-" * 60)
            print("데이터 미리보기 (처음 5개):")
            print("-" * 60)
            print(df.head().to_string())

            print("\n" + "-" * 60)
            print("데이터 통계:")
            print("-" * 60)
            print(df.describe().to_string())

        else:
            print("\n✗ 데이터를 추출하지 못했습니다.")
            print("다음을 확인해주세요:")
            print("1. 인터넷 연결")
            print("2. CryptoQuant 사이트 접근 가능 여부")
            print("3. Chrome/ChromeDriver 설치 상태")

    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("1. requirements.txt의 모든 패키지가 설치되었는지 확인")
        print("2. Chrome 브라우저가 설치되었는지 확인")
        print("3. ChromeDriver가 올바르게 설치되었는지 확인")

    finally:
        # 정리
        scraper.close()
        print("\n" + "=" * 60)
        print("프로그램 종료")
        print("=" * 60)


if __name__ == "__main__":
    main()
