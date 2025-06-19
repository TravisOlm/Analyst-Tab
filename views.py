from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import traceback
from datetime import datetime
from MomentumSim.data_fetching import get_historical_data, fetch_multiple_historical_data
from API.UpdateUserData import fetch_updated_data
from API.AITools import (
    summarize_portfolio, sector_total, get_total_dividends, get_recommendations,
    analyse_volume_change, get_volatility_and_sharpe, get_monthly_performance, get_stock_info
)
from ScrapeData.helpers import run_news_sentiment
from Vision.VisHelper import run_vision_model_analysis  # you likely already have this helper now!
from PortfolioGraphs.PortfolioAllLines import get_multi_stock_graph_json

# Import it at the top:
from .Summary import summarize_stock, summary_portfolio

# new features 
from .health_analysis import get_health_response
from .analyst_opinion import get_opinions_response
from .Business_analysis import get_business_response


@csrf_exempt
def comprehensive_summary(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        payload = json.loads(request.body)
        user_id = payload.get("user_id", 1)
        mode = payload.get("mode", "portfolio")  # default
        ticker = payload.get("ticker", "").upper()
        start_date = payload.get("start_date", "2022-01-01")
        end_date = payload.get("end_date", datetime.now().strftime("%Y-%m-%d"))

        
        results = {
            "mode": mode,
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }

        if mode != "single_stock":
            return JsonResponse({"error": "Only 'single_stock' mode is supported."}, status=400)


        elif mode == "single_stock" and ticker:
            # Single Stock mode
            df = get_historical_data(ticker, start_date, end_date)

            # Vision model (cleaned)
            vision_result_raw = run_vision_model_analysis(ticker, start_date, end_date, indicators=["20-Day SMA", "VWAP", "20-Day Bollinger Bands", "20-Day EMA"])
            vision_result_clean = {}

            if vision_result_raw and "results" in vision_result_raw and len(vision_result_raw["results"]) > 0:
                vision_data = vision_result_raw["results"][0]

                vision_result_clean = {
                    "ticker": vision_data.get("ticker", ""),
                    "analysis": vision_data.get("analysis", {})  # No chart_json here
                }

            results["vision_model"] = vision_result_clean

            # Stock AI tools
            results["stock_ai"] = {
                #"volume": analyse_volume_change.invoke({"stock": ticker}),
                "volatility_sharpe": get_volatility_and_sharpe.invoke({"ticker": ticker}),
                "basic_info": get_stock_info.invoke({"stock": ticker, "field": "market cap"})
            }

            # News sentiment for single stock
            results["news_sentiment"] = run_news_sentiment(ticker)

            results["llm_insights"] = {
                "health_analysis": get_health_response(ticker),
                "analyst_opinion": get_opinions_response(ticker),
                "business_analysis": get_business_response(ticker)
            }

            # LLM summary of info 
            stock_summary_text = summarize_stock(
                ticker,
                vision_result_clean.get("analysis", {}),
                results["stock_ai"],
                results["news_sentiment"],
                health_text=results["llm_insights"]["health_analysis"],
                business_text=results["llm_insights"]["business_analysis"],
                analyst_opinion_text=results["llm_insights"]["analyst_opinion"]
            )

            results["stock_summary"] = {
                "ticker": ticker,
                "summary": stock_summary_text
            }


        else:
            return JsonResponse({"error": "Invalid mode or missing ticker"}, status=400)

        # Optional timestamp
        from datetime import timezone
        results["timestamp"] = datetime.now(timezone.utc).isoformat()

        return JsonResponse(results)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def summarize_risk_metrics(request):
    import requests
    import json

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        risk_metrics = data.get("risk_metrics", {})

        volume_text = risk_metrics.get("volume_text", "")
        volatility_text = risk_metrics.get("volatility_text", "")
        market_cap_text = risk_metrics.get("market_cap_text", "")

        summary_prompt = (f"""
        Here is stock risk data:

        Volume Data:
        {volume_text}

        Volatility & Sharpe Ratio:
        {volatility_text}

        Market Cap:
        {market_cap_text}

        Please clearly and accurately summarize this data.
        ONLY use numbers and insights actually present.
        DO NOT make up comparisons to historical norms unless provided.
        DO NOT explain what a Sharpe ratio is — just interpret the value.
        DO NOT treat market cap as a risk factor.

        Highlight actionable insights for an investor.
        """)

        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:latest",  # or your favorite model
                "prompt": summary_prompt,
                "stream": False,
                "num_ctx": 32000  # Adjust context size as needed

            },
            timeout=120
        )
        summary = response.json().get("response", "").strip()

        return JsonResponse({"summary": summary})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def portfolio_breakdown(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        payload = json.loads(request.body)
        user_id = int(payload.get("user_id", 1))

        portfolio_data = fetch_updated_data(user_id=user_id)
        portfolio_symbols = [x["symbol"] for x in portfolio_data if x.get("symbol")]

        results = { "user_id": user_id, "stocks": [] }

        for symbol in portfolio_symbols:
            try:
                vision = run_vision_model_analysis(symbol, "2022-01-01", datetime.now().strftime("%Y-%m-%d"),
                                                   indicators=["20-Day SMA", "VWAP", "20-Day EMA", "20-Day Bollinger Bands"])
                vision_analysis = vision.get("results", [{}])[0].get("analysis", {})

                stock_ai = {
                    "volume": analyse_volume_change.invoke({"stock": symbol}),
                    "volatility_sharpe": get_volatility_and_sharpe.invoke({"ticker": symbol}),
                    "basic_info": get_stock_info.invoke({"stock": symbol, "field": "market cap"})
                }

                news = run_news_sentiment(symbol)

                summary = summarize_stock(symbol, vision_analysis, stock_ai, news)

                results["stocks"].append({
                    "symbol": symbol,
                    "summary": summary,
                    "vision_analysis": vision_analysis,
                    "stock_ai": stock_ai,
                    "news_sentiment": news
                })

            except Exception as e:
                results["stocks"].append({
                    "symbol": symbol,
                    "error": str(e)
                })

        return JsonResponse(results)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


