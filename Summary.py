# API/Summary.py

import requests
import json

OLLAMA_MODEL = "qwen2.5"  # You can easily change this if needed later


def summarize_stock(ticker, vision_analysis, stock_ai, news_sentiment, health_text, business_text, analyst_opinion_text):
    """
    Generates a holistic summary for a single stock.

    Args:
        ticker (str): Stock ticker
        vision_analysis (dict): Vision model analysis
        stock_ai (dict): Dict with volume, volatility_sharpe, basic_info
        news_sentiment (dict): News sentiment result

    Returns:
        str: Stock summary text
    """
    stock_prompt = f"""
You are a financial research assistant. Summarize the investment outlook for {ticker} based on the following structured data sources.

Provide a well-organized response covering these key areas:
🔍 1. Business Model & Competitive Advantage
- What products/services does the company offer, and who are its main customers?
- Does it have a moat (brand, IP, network effects, switching costs)?
- Is the business diversified across products/regions, or reliant on a few?

📈 2. Industry & Market Trends
- Is the company in a growing or shrinking industry?
- How sensitive is its revenue to economic cycles?
- Are there emerging regulatory risks (e.g., antitrust, ESG)?

🧠 3. Management & Governance
- Describe the leadership team's experience and credibility.
- Does the board have independent oversight or is it tightly controlled?
- Is capital being allocated efficiently (e.g., buybacks, R&D, M&A)?

💵 4. Valuation Metrics
- Interpret the stock’s valuation (P/E, PEG, EV/EBITDA, P/S).
- Compare it to peers, historical averages, and growth expectations.

📊 5. Technical Indicators (Short/Medium Term)
- Note trend direction and strength using SMA/EMA, RSI, MACD.
- Highlight support/resistance zones or unusual price/volume moves.

🧨 6. Risk Factors
- Debt profile and refinancing risks.
- Exposure to FX rates, legal troubles, or ESG controversies.
- Dependency on few customers/suppliers.

📚 7. Sentiment & Analyst Coverage
- What's the recent tone in media or investor sentiment?
- What do analysts project (ratings, targets, earnings surprises)?

--- TECHNICAL ANALYSIS ---
{json.dumps(vision_analysis, indent=2)}

--- RISK METRICS ---
{stock_ai.get('volume', 'N/A')}
{stock_ai.get('volatility_sharpe', 'N/A')}
{stock_ai.get('basic_info', 'N/A')}

--- NEWS SENTIMENT ---
{json.dumps(news_sentiment, indent=2)}

--- BUSINESS OVERVIEW ---
{business_text or 'N/A'}

--- FINANCIAL HEALTH ---
{health_text or 'N/A'}

--- ANALYST OPINION ---
{analyst_opinion_text or 'N/A'}
"""

    # Ensure the prompt is not too long
    print(len(stock_prompt))
    if len(stock_prompt) > 32000:
        print("Truncating stock prompt to fit within context size")
        stock_prompt = stock_prompt[:32000]  # Truncate if necessary

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": stock_prompt,
                "stream": False,
                "options":{
                    "num_ctx": 32000
                }  # Adjust context size as needed

            },
            timeout=240
        )
        summary_text = response.json().get("response", "").strip()
    except Exception as e:
        summary_text = f"Stock summary generation failed: {str(e)}"

    return summary_text


def summary_portfolio(portfolio_ai, news_sentiment):
    """
    Generates a holistic summary for the user's portfolio.

    Args:
        portfolio_ai (dict): Dict with summary, sector, dividends, recommendations
        news_sentiment (dict): News sentiment result

    Returns:
        str: Portfolio summary text
    """
    portfolio_prompt = f"""
        You are a financial assistant. Based on the following portfolio analysis, provide a clear 4-6 bullet point summary covering:

        1. Portfolio performance trends
        2. Sector distribution insights
        3. Dividend income highlights
        4. Notable analyst recommendations
        5. General investment outlook and risks

        --- PORTFOLIO SUMMARY ---
        {portfolio_ai.get('summary', 'N/A')}

        --- SECTOR TOTALS ---
        {portfolio_ai.get('sector', 'N/A')}

        --- DIVIDENDS ---
        {portfolio_ai.get('dividends', 'N/A')}

        --- RECOMMENDATIONS ---
        {portfolio_ai.get('recommendations', 'N/A')}

        --- NEWS SENTIMENT ---
        {json.dumps(news_sentiment, indent=2)}
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": portfolio_prompt,
                "stream": False,
                "num_ctx": 32000  # Adjust context size if needed
            },
            timeout=240
        )
        summary_text = response.json().get("response", "").strip()
    except Exception as e:
        summary_text = f"Portfolio summary generation failed: {str(e)}"

    return summary_text
