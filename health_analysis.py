import yfinance as yf
import pandas as pd
import datetime as dt
import requests 
import json
from .fetch_info import safe_get_info


def _is_valid(value):
    """Return True if the value is usable in a prompt."""
    return value not in (None, "N/A", "None")


def _has_valid_data(*values):
    """Return True if any provided value is valid."""
    return any(_is_valid(v) for v in values)

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

    metrics = [
        profit_margin, gross_margin, return_on_assets,
        earnings_growth, revenue_growth,
        enterprice_to_revenue, total_debt, debt_to_equity,
        total_revenue, market_cap, pe_ratio, forward_pe_ratio,
        price_to_book, current_ratio, quick_ratio,
        free_cashflow, operating_cashflow, Insiders, Institutions,
    ]

    if not _has_valid_data(*metrics):
        return None

    def fmt_line(label, value):
        return f"- {label}: {value}" if _is_valid(value) else None

    profit_lines = list(filter(None, [
        fmt_line("Profit Margin", profit_margin),
        fmt_line("Gross Margin", gross_margin),
        fmt_line("Return on Assets", return_on_assets),
    ]))

    growth_lines = list(filter(None, [
        fmt_line("Earnings Growth", earnings_growth),
        fmt_line("Revenue Growth", revenue_growth),
    ]))

    efficiency_lines = list(filter(None, [
        fmt_line("Enterprise to Revenue Ratio", enterprice_to_revenue),
    ]))

    debt_lines = list(filter(None, [
        fmt_line("Total Debt", total_debt),
        fmt_line("Debt to Equity Ratio", debt_to_equity),
    ]))

    size_lines = list(filter(None, [
        fmt_line("Total Revenue", total_revenue),
        fmt_line("Market Cap", market_cap),
    ]))

    valuation_lines = list(filter(None, [
        fmt_line("P/E Ratio", pe_ratio),
        fmt_line("Forward P/E Ratio", forward_pe_ratio),
        fmt_line("Price to Book Ratio", price_to_book),
    ]))

    liquidity_lines = list(filter(None, [
        fmt_line("Current Ratio", current_ratio),
        fmt_line("Quick Ratio", quick_ratio),
    ]))

    cash_lines = list(filter(None, [
        fmt_line("Free Cash Flow", free_cashflow),
        fmt_line("Operating Cash Flow", operating_cashflow),
    ]))

    ownership_lines = list(filter(None, [
        fmt_line("Insider Holdings", Insiders),
        fmt_line("Institutional Holdings", Institutions),
    ]))

    profit_section = "\n".join(profit_lines)
    growth_section = "\n".join(growth_lines)
    efficiency_section = "\n".join(efficiency_lines)
    debt_section = "\n".join(debt_lines)
    size_section = "\n".join(size_lines)
    valuation_section = "\n".join(valuation_lines)
    liquidity_section = "\n".join(liquidity_lines)
    cash_section = "\n".join(cash_lines)
    ownership_section = "\n".join(ownership_lines)

    health_prompt = f"""
You are a accountant tasked with evaluating the financial health of {ticker} based on its stock data.

Profitability Metrics:
{profit_section}

Growth Metrics:
{growth_section}

Efficiency Metrics:
{efficiency_section}

Debt Metrics:
{debt_section}

Size Metrics:
{size_section}

Valuation Metrics:
{valuation_section}

Liquidity Metrics:
{liquidity_section}

Cash Flow Metrics:
{cash_section}

Ownership Metrics:
{ownership_section}

Based on the metrics given above, provide a detailed and structured analysis of {ticker}'s financial health.

Please highlight:
1. Key strengths and weaknesses
2. Areas of risk or concern (e.g., liquidity, high debt)
3. Overall outlook (positive/neutral/negative)
    """


    print(health_prompt)

    return health_prompt

def get_health_response(ticker) -> str:
    prompt = fetch_health_prompt(ticker)
    if not prompt:
        return "Health data not available."

    try:
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:latest",  # or your favorite model
                "prompt": prompt,
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
