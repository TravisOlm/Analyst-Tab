import yfinance as yf
import pandas as pd
import datetime as dt
import requests 
import json
from .fetch_info import safe_get_info

def fetch_opinions_prompt(ticker):
    
    tick = safe_get_info(ticker)


    #data 

    recommendation = tick.get("recommendationKey", "unknown")
    analysts = tick.get("numberOfAnalystOpinions", 0)
    recommendation_mean = tick.get("recommendationMean", "N/A")

    target_mean = tick.get("targetMeanPrice")
    target_median = tick.get("targetMedianPrice")
    avg_rating = tick.get("averageAnalystRating")

    pe_forward = tick.get("forwardPE")
    peg_ratio = tick.get("trailingPegRatio")
    eps_fwd = tick.get("epsForward")

    analysts_prompt = f"""
You are a financial analyst tasked with evaluating the stock recommendations for {ticker} based on analyst opinions.

Analyst Recommendations:
- Recommendation: {recommendation}
- Average Rating: {avg_rating}
- Number of Analysts: {analysts}
- Recommendation Mean: {recommendation_mean}

Target Price Range:
- High: {tick.get("targetHighPrice")}
- Low: {tick.get("targetLowPrice")}
- Mean: {target_mean}
- Median: {target_median}

Valuation Metrics:
- Forward PE Ratio: {pe_forward}
- PEG Ratio: {peg_ratio}
- EPS Forward: {eps_fwd}

Please provide a detailed analysis of the stock's potential based on these recommendations, valuation metrics, and price targets.
"""

    print(analysts_prompt)

    return analysts_prompt

def get_opinions_response(ticker) -> str: 
        
    try: 
        # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:latest",  # or your favorite model
                    "prompt": fetch_opinions_prompt(ticker),
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
