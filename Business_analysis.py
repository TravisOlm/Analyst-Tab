import yfinance as yf
import pandas as pd
import datetime as dt
import requests 
import json
from .fetch_info import safe_get_info

def fetch_business_prompt(ticker):
    
    tick = safe_get_info(ticker)


    industry = tick.get('industry', 'N/A')
    sector = tick.get('sector', 'N/A')
    business_summary = tick.get('longBusinessSummary', 'N/A')
    country = tick.get('country', 'N/A')
    employees = tick.get('fullTimeEmployees', 'N/A')

    # Define relevant title keywords
    relevant_titles = [
        "chief executive", "ceo", "co-founder", "founder",
        "chief financial", "cfo", 
        "president", "vp", "vice president",
        "chief designer", "design", 
        "vehicle engineering", "apac", "asia", "technology"
    ]

    # Fetch and filter relevant officers
    officer_list = tick.get('companyOfficers', [])
    filtered_officers = []

    def format_number(value):
        return f"${value:,.0f}" if isinstance(value, (int, float)) else "N/A"

    for officer in officer_list:
        title = officer.get('title', '').lower()
        
        # Check if the title contains any of the relevant keywords
        if any(keyword in title for keyword in relevant_titles):
            name = officer.get('name', 'N/A')
            formatted_title = officer.get('title', 'N/A')
            age = officer.get('age', 'N/A')
            total_pay = format_number(officer.get('totalPay'))
            exercised = format_number(officer.get('exercisedValue'))
            unexercised = format_number(officer.get('unexercisedValue'))

            filtered_officers.append(
                f"- {name} ({formatted_title}) | Age: {age}, "
                f"Total Pay: {total_pay}, Exercised: {exercised}, Unexercised: {unexercised}"
            )

    officers_section = "\n".join(filtered_officers) if filtered_officers else "Key executive information not available."

    bussiness_prompt = f"""
You are a finacial analyst tasked with evaluating and explaining {ticker} based on the company’s core business and whether it has a sustainable competitive advantage.

Business Overview: 
- Industry: {industry}
- Sector: {sector}
- Country: {country}
- Employees: {employees}

Business Summary: {business_summary}

Key Executives:
{officers_section}

Your task is to analyze the company's business model, its competitive position in the market, and its potential for long-term growth. Consider the following aspects:
1. **Industry Analysis**: What is the current state of the industry in which the company operates? Are there any trends or challenges that could impact the company's performance?
2. **Competitive Advantage**: Does the company have a sustainable competitive advantage? What differentiates it from its competitors?
3. **Market Position**: How does the company position itself in the market? Is it a leader, challenger, or niche player?
    """


    print(bussiness_prompt)

    return bussiness_prompt

def get_business_response(ticker) -> str: 
        
    try: 
        # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:latest",  # or your favorite model
                    "prompt": fetch_business_prompt(ticker),
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
