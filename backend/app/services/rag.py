# backend/app/services/rag.py

def synthesize_report(ticker, fundamentals, prices, news, sentiment, prediction):
    return f"""
### Stock Analysis Report: {ticker.upper()}

**Company:** {fundamentals.get("name", "N/A")}
**Sector:** {fundamentals.get("sector", "N/A")}
**Industry:** {fundamentals.get("industry", "N/A")}
**Market Cap:** {fundamentals.get("market_cap", "N/A")}
**P/E Ratio:** {fundamentals.get("pe_ratio", "N/A")}
**EPS:** {fundamentals.get("eps", "N/A")}
**Debt/Equity:** {fundamentals.get("de_ratio", "N/A")}

### Sentiment
Average news sentiment score: {sentiment["average_sentiment"]}

### Price Prediction (next {prediction["horizon_days"]} days)
{prediction["predictions"]}
"""
