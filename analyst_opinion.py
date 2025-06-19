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

def fetch_opinions_prompt(ticker):
    
    tick = safe_get_info(ticker)


    #data 

    recommendation = tick.get("recommendationKey", "unknown")
    analysts = tick.get("numberOfAnalystOpinions", 0)
    recommendation_mean = tick.get("recommendationMean", "N/A")

    target_mean = tick.get("targetMeanPrice")
    target_median = tick.get("targetMedianPrice")
    target_high = tick.get("targetHighPrice")
    target_low = tick.get("targetLowPrice")
    avg_rating = tick.get("averageAnalystRating")

    pe_forward = tick.get("forwardPE")
    peg_ratio = tick.get("trailingPegRatio")
    eps_fwd = tick.get("epsForward")

    metrics = [
        recommendation, analysts, recommendation_mean,
        target_mean, target_median, avg_rating,
        pe_forward, peg_ratio, eps_fwd,
        target_high, target_low
    ]

    if not _has_valid_data(*metrics):
        return None

    rec_lines = []
    if _is_valid(recommendation):
        rec_lines.append(f"- Recommendation: {recommendation}")
    if _is_valid(avg_rating):
        rec_lines.append(f"- Average Rating: {avg_rating}")
    if _is_valid(analysts):
        rec_lines.append(f"- Number of Analysts: {analysts}")
    if _is_valid(recommendation_mean):
        rec_lines.append(f"- Recommendation Mean: {recommendation_mean}")

    price_lines = []
    if _is_valid(target_high):
        price_lines.append(f"- High: {target_high}")
    if _is_valid(target_low):
        price_lines.append(f"- Low: {target_low}")
    if _is_valid(target_mean):
        price_lines.append(f"- Mean: {target_mean}")
    if _is_valid(target_median):
        price_lines.append(f"- Median: {target_median}")

    val_lines = []
    if _is_valid(pe_forward):
        val_lines.append(f"- Forward PE Ratio: {pe_forward}")
    if _is_valid(peg_ratio):
        val_lines.append(f"- PEG Ratio: {peg_ratio}")
    if _is_valid(eps_fwd):
        val_lines.append(f"- EPS Forward: {eps_fwd}")

    rec_section = "\n".join(rec_lines)
    price_section = "\n".join(price_lines)
    val_section = "\n".join(val_lines)

    analysts_prompt = f"""
You are a financial analyst tasked with evaluating the stock recommendations for {ticker} based on analyst opinions.

Analyst Recommendations:
{rec_section}

Target Price Range:
{price_section}

Valuation Metrics:
{val_section}

Please provide a detailed analysis of the stock's potential based on these recommendations, valuation metrics, and price targets.
"""

    print(analysts_prompt)

    return analysts_prompt

def get_opinions_response(ticker) -> str:
    prompt = fetch_opinions_prompt(ticker)
    if not prompt:
        return "Analyst opinion data not available."

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
