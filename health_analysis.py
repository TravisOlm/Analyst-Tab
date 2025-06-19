import yfinance as yf
import pandas as pd
import datetime as dt
import requests 
import json
from .fetch_info import safe_get_info

def fetch_health_prompt(ticker):
    
    tick = safe_get_info(ticker)

    #profitablity 
    profit_margin = tick.get('profitMargins', 'N/A')
    gross_margin = tick.get('grossMargins', 'N/A')
    return_on_assets = tick.get('returnOnAssets', 'N/A')

    #Growth 
    earnings_growth = tick.get('earningsGrowth', 'N/A')
    revenue_growth = tick.get('revenueGrowth', 'N/A')

    #efficiency 
    enterprice_to_revenue = tick.get('enterpriseToRevenue', 'N/A')

    #Debt 
    total_debt = tick.get('totalDebt', 'N/A')
    debt_to_equity = tick.get('debtToEquity', 'N/A')

    # Size 
    total_revenue = tick.get('totalRevenue', 'N/A')
    market_cap = tick.get('marketCap', 'N/A')


    # Ownership - who owns shares 
    Insiders = tick.get("heldPercentInsiders", "N/A")
    Institutions = tick.get("heldPercentInstitutions", "N/A")

    # Valuation - Gives the model insight into how the market values the company’s earnings.
    pe_ratio = tick.get("trailingPE", "N/A")
    forward_pe_ratio = tick.get("forwardPE", "N/A")
    price_to_book = tick.get("priceToBook", "N/A") 

    # liquidity - 1.2 to 2 is considered healthy 
    current_ratio = tick.get("currentRatio", "N/A") # assets including inventory
    quick_ratio = tick.get("quickRatio", "N/A") # easily liquid assets 

    # Cash flow
    free_cashflow = tick.get("freeCashflow", "N/A")
    operating_cashflow = tick.get("operatingCashflow", "N/A")

    # Ownership - who owns shares 
    Insiders = tick.get("heldPercentInsiders", "N/A")
    Institutions = tick.get("heldPercentInstitutions", "N/A")

    health_prompt = f"""
You are a accountant tasked with evaluating the financial health of {ticker} based on its stock data.

Profitability Metrics:
- Profit Margin: {profit_margin}
- Gross Margin: {gross_margin}
- Return on Assets: {return_on_assets}

Growth Metrics:
- Earnings Growth: {earnings_growth}
- Revenue Growth: {revenue_growth}

Efficiency Metrics:
- Enterprise to Revenue Ratio: {enterprice_to_revenue}

Debt Metrics:
- Total Debt: {total_debt}
- Debt to Equity Ratio: {debt_to_equity}

Size Metrics:
- Total Revenue: {total_revenue}
- Market Cap: {market_cap}

Valuation Metrics:
- P/E Ratio: {pe_ratio}
- Forward P/E Ratio: {forward_pe_ratio}
- Price to Book Ratio: {price_to_book}

Liquidity Metrics:
- Current Ratio: {current_ratio}
- Quick Ratio: {quick_ratio}

Cash Flow Metrics:
- Free Cash Flow: {free_cashflow}
- Operating Cash Flow: {operating_cashflow}

Ownership Metrics:
- Insider Holdings: {Insiders}
- Institutional Holdings: {Institutions}

Based on the metrics given above, provide a detailed and structured analysis of {ticker}'s financial health.

Please highlight:
1. Key strengths and weaknesses 
2. Areas of risk or concern (e.g., liquidity, high debt)
3. Overall outlook (positive/neutral/negative)
    """


    print(health_prompt)

    return health_prompt

def get_health_response(ticker) -> str: 
        
    try: 
        # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:latest",  # or your favorite model
                    "prompt": fetch_health_prompt(ticker),
                    "stream": False,
                    "num_ctx": 32000  # Adjust context size as needed

                },
                timeout=120
            )
            summary = response.json().get("response", "").strip()
            return summary

    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        summary = "Failed to generate summary due to an error."
        return summary
