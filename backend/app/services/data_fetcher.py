import os
from datetime import datetime, timedelta
import yfinance as yf
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

if NEWSAPI_KEY:
    newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
else:
    newsapi = None

def get_financial_trends(stock):
    """
    Helper to extract growth trends from quarterly financials.
    Returns a summary string and raw metric lists.
    """
    try:
        # Get last 4 quarters of data
        q_fin = stock.quarterly_financials
        if q_fin is None or q_fin.empty:
            return {"note": "No quarterly data available"}

        # Extract Revenue & Net Income
        # yfinance rows are labeled 'Total Revenue' or 'Operating Revenue' depending on the sector
        rev_row = 'Total Revenue' if 'Total Revenue' in q_fin.index else 'Operating Revenue'
        
        # Safety check if rows exist
        if rev_row not in q_fin.index or 'Net Income' not in q_fin.index:
            return {"note": "Incomplete financial rows"}

        revenues = q_fin.loc[rev_row].values[:4]  # Newest to oldest
        incomes = q_fin.loc['Net Income'].values[:4]

        # Calculate Margins (Net Income / Revenue)
        margins = []
        for r, i in zip(revenues, incomes):
            if r > 0:
                margins.append(round((i / r) * 100, 2))
            else:
                margins.append(0)

        # Calculate Revenue Growth (Current Q vs Same Q Last Year if possible, or Q-over-Q)
        # Simple Q-over-Q for recent trend: (Newest - Previous) / Previous
        if len(revenues) >= 2 and revenues[1] > 0:
            rev_growth_qoq = ((revenues[0] - revenues[1]) / revenues[1]) * 100
        else:
            rev_growth_qoq = 0

        return {
            "recent_quarterly_revenue": [f"${x/1e9:.2f}B" for x in revenues],
            "recent_profit_margins": [f"{m}%" for m in margins],
            "revenue_growth_last_q": f"{rev_growth_qoq:+.2f}%",
            "trend_direction": "Growing" if rev_growth_qoq > 0 else "Declining"
        }
    except Exception as e:
        return {"error": f"Trend calc failed: {str(e)}"}


async def fetch_fundamentals(ticker: str):
    """
    Fetches company fundamentals using yfinance.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    if not info or "regularMarketPrice" not in info:
        return {"error": "Invalid ticker or no data available."}
    
    trends = get_financial_trends(stock)

    return {
        "symbol": ticker.upper(),
        "name": info.get("longName", info.get("shortName", ticker)),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "de_ratio": info.get("debtToEquity"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "financial_trends": trends
    }


async def fetch_price_history(ticker: str, days: int = 365):
    """
    Fetches historical daily close prices.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=f"{days}d")

    if data.empty:
        return []

    return [
        {"date": str(index.date()), "close": round(float(row["Close"]), 2)}
        for index, row in data.iterrows()
    ]


def fetch_news_docs(ticker: str, limit: int = 25):
    if newsapi is None:
        return [{"error": "NEWSAPI_KEY not set"}]
    
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=14)

    # Query both ticker & company name keywords
    query = f"{ticker} stocks"

    articles = newsapi.get_everything(
        q=query,
        language="en",
        page_size=limit,
        from_param=from_date.strftime("%Y-%m-%d"),
        to=to_date.strftime("%Y-%m-%d")
    )
    print(articles)
    result = []
    for article in articles.get("articles", []):
        result.append({
            "title": article["title"],
            "source": article["source"]["name"],
            "url": article["url"],
            "published_at": article["publishedAt"],
            "content": article["description"]
        })

    return result


async def fetch_news_docs(ticker: str, limit: int = 25):
    import asyncio
    return await asyncio.to_thread(fetch_news_docs, ticker, limit)