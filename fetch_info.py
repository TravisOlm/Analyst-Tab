import time
import yfinance as yf
from urllib.error import HTTPError

def safe_get_info(ticker_symbol, max_retries=5, delay=1):
    """
    Retry-safe yfinance info fetch that handles HTTP 401 errors.
    """
    for attempt in range(max_retries):
        try:
            tick = yf.Ticker(ticker_symbol)
            info = tick.info
            if info:  # Ensure we got valid data
                return info
        except HTTPError as e:
            if "401" in str(e):
                print(f"[Retry {attempt+1}] HTTP 401 error for {ticker_symbol}, retrying...")
                time.sleep(delay)
                continue
            else:
                raise
        except Exception as e:
            print(f"[Retry {attempt+1}] Unexpected error: {e}, retrying...")
            time.sleep(delay)

    print(f"❌ Failed to fetch data for {ticker_symbol} after {max_retries} retries.")
    return {}
