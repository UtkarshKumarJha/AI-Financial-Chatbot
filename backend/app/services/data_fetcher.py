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


async def fetch_fundamentals(ticker: str):
    """
    Fetches company fundamentals using yfinance.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    if not info or "regularMarketPrice" not in info:
        return {"error": "Invalid ticker or no data available."}

    return {
        "symbol": ticker.upper(),
        "name": info.get("longName", info.get("shortName", ticker)),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "de_ratio": info.get("debtToEquity"),
        "sector": info.get("sector"),
        "industry": info.get("industry")
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


async def fetch_news_docs(ticker: str, limit: int = 25):
    """
    Fetches recent news articles related to the ticker.
    Uses NewsAPI query search.
    """
    if newsapi is None:
        return [{"error": "NEWSAPI_KEY not set"}]

    # Query both ticker & company name keywords
    query = f"{ticker}"

    articles = newsapi.get_everything(
        q=query,
        language="en",
        page_size=limit
    )

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
